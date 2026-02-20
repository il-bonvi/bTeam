/**
 * bTeam WebApp - omniPD Model Calculator
 * Critical Power model based on omniPD formula
 */

// Constants
const TCPMAX = 1800; // 30 minutes

/**
 * Calculate power at time t using omniPD model
 * Formula: P(t) = (W'/t) × (1 - e^(-t × (Pmax - CP) / W')) + CP for t ≤ 1800s
 *          P(t) = above - A × ln(t / 1800) for t > 1800s
 */
function ompd_power(t, CP, W_prime, Pmax, A) {
    const base = (W_prime / t) * (1 - Math.exp(-t * (Pmax - CP) / W_prime)) + CP;
    return t <= TCPMAX ? base : base - A * Math.log(t / TCPMAX);
}

/**
 * Calculate effective W' at time t
 */
function w_eff(t, W_prime, CP, Pmax) {
    return W_prime * (1 - Math.exp(-t * (Pmax - CP) / W_prime));
}

/**
 * Format time in seconds to readable label
 */
function formatTimeLabel(seconds) {
    seconds = Math.round(seconds);
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0 && minutes % 60 === 0 && secs === 0) {
        return `${hours}h`;
    } else if (minutes > 0 && secs === 0) {
        return `${minutes}m`;
    } else if (minutes > 0) {
        return `${minutes}m${secs}s`;
    } else {
        return `${seconds}s`;
    }
}

/**
 * Calculate squared error for optimization
 */
function calculateError(params, timeValues, powerValues) {
    let sumSquaredError = 0;
    for (let i = 0; i < timeValues.length; i++) {
        const predicted = ompd_power(timeValues[i], ...params);
        const error = powerValues[i] - predicted;
        sumSquaredError += error * error;
    }
    return sumSquaredError;
}

/**
 * Fit omniPD curve to data using Nelder-Mead optimization
 */
function curveFit(timeValues, powerValues) {
    // Initial parameter estimates
    const sortedPower = [...powerValues].sort((a, b) => a - b);
    const CP_init = sortedPower[Math.floor(sortedPower.length * 0.3)];
    const W_prime_init = 20000;
    const Pmax_init = Math.max(...powerValues);
    const A_init = 5;

    let params = [CP_init, W_prime_init, Pmax_init, A_init];
    
    // Simplified Nelder-Mead optimization
    const maxIter = 1000;
    let step = [10, 1000, 10, 0.5];
    
    for (let iter = 0; iter < maxIter; iter++) {
        const currentError = calculateError(params, timeValues, powerValues);
        let improved = false;

        for (let i = 0; i < params.length; i++) {
            const testParams = [...params];
            testParams[i] += step[i];
            const testError = calculateError(testParams, timeValues, powerValues);
            
            if (testError < currentError) {
                params = testParams;
                improved = true;
            } else {
                testParams[i] = params[i] - step[i];
                const testError2 = calculateError(testParams, timeValues, powerValues);
                if (testError2 < currentError) {
                    params = testParams;
                    improved = true;
                }
            }
        }

        if (!improved) {
            step = step.map(s => s * 0.9);
        }
        
        if (step.every(s => Math.abs(s) < 0.01)) break;
    }

    return params;
}

/**
 * Filter power curve data using time windows and percentile threshold
 * @param {Array} allTimes - Raw time data
 * @param {Array} allPowers - Raw power data
 * @param {Number} valuesPerWindow - Number of values to select per window
 * @param {Number} minPercentile - Minimum percentile threshold (0-100)
 * @param {Number} sprintSeconds - Sprint duration for sprint point selection
 * @returns {Object} {times: [], powers: [], selectedCount: Number}
 */
function filterPowerCurveData(allTimes, allPowers, valuesPerWindow, minPercentile, sprintSeconds) {
    if (allTimes.length < 4) {
        return { times: allTimes, powers: allPowers, selectedCount: allTimes.length };
    }

    // First fit to get residuals
    const params = curveFit(allTimes, allPowers);
    const predictions = allTimes.map((t) => ompd_power(t, ...params));
    const residuals = allPowers.map((p, i) => p - predictions[i]);

    // Calculate percentile threshold using numpy-style linear interpolation
    const residualsClean = residuals.filter(r => !isNaN(r));
    let percentileThreshold = -Infinity;
    if (residualsClean.length > 0) {
        residualsClean.sort((a, b) => a - b);
        // Use numpy linear interpolation method for percentile calculation
        const h = (residualsClean.length - 1) * (minPercentile / 100);
        const floor_idx = Math.floor(h);
        const ceil_idx = Math.ceil(h);
        const frac = h - floor_idx;
        
        if (floor_idx === ceil_idx) {
            percentileThreshold = residualsClean[floor_idx];
        } else {
            percentileThreshold = residualsClean[floor_idx] * (1 - frac) + residualsClean[ceil_idx] * frac;
        }
        if (isNaN(percentileThreshold)) {
            percentileThreshold = Math.min(...residualsClean);
        }
    }

    // Define time windows: 2-minute intervals from 2-30 min, then 15-minute intervals to 90 min
    const timeWindows = [];
    for (let start = 120; start < 1800; start += 120) {
        timeWindows.push([start, start + 120]);
    }
    for (let start = 1800; start < 5400; start += 900) {
        timeWindows.push([start, start + 900]);
    }

    let selectedTimes = [];
    let selectedPowers = [];
    let selectedMask = new Array(allTimes.length).fill(false);

    // Select points from each window
    for (const [tmin, tmax] of timeWindows) {
        const windowIndices = [];
        for (let i = 0; i < allTimes.length; i++) {
            if (allTimes[i] >= tmin && allTimes[i] <= tmax) {
                windowIndices.push(i);
            }
        }
        if (windowIndices.length === 0) continue;

        // Sort by residual descending
        const sortedIndices = windowIndices.sort((a, b) => residuals[b] - residuals[a]);

        // Take up to valuesPerWindow where residual >= threshold
        let count = 0;
        for (const i of sortedIndices) {
            if (!isNaN(residuals[i]) && residuals[i] >= percentileThreshold && !selectedMask[i]) {
                selectedTimes.push(allTimes[i]);
                selectedPowers.push(allPowers[i]);
                selectedMask[i] = true;
                count++;
                if (count >= valuesPerWindow) break;
            }
        }
    }

    // Add sprint point if specified
    if (sprintSeconds > 0) {
        let minDist = Infinity;
        let sprintIdx = -1;
        for (let i = 0; i < allTimes.length; i++) {
            const dist = Math.abs(allTimes[i] - sprintSeconds);
            if (dist < minDist) {
                minDist = dist;
                sprintIdx = i;
            }
        }
        if (sprintIdx >= 0 && !selectedMask[sprintIdx]) {
            selectedTimes.push(allTimes[sprintIdx]);
            selectedPowers.push(allPowers[sprintIdx]);
            selectedMask[sprintIdx] = true;
        }
    }

    // Sort by time
    const sortedIndices = selectedTimes.map((_, i) => i).sort((a, b) => selectedTimes[a] - selectedTimes[b]);
    selectedTimes = sortedIndices.map(i => selectedTimes[i]);
    selectedPowers = sortedIndices.map(i => selectedPowers[i]);

    return {
        times: selectedTimes,
        powers: selectedPowers,
        selectedCount: selectedTimes.length,
        totalCount: allTimes.length
    };
}

/**
 * Calculate omniPD parameters and statistics
 */
function calculateOmniPD(timeValues, powerValues) {
    if (timeValues.length < 4) {
        throw new Error('Insufficienti dati: servono almeno 4 punti');
    }

    // Fit model
    const params = curveFit(timeValues, powerValues);
    
    // If no data beyond TCPMAX, set A = 5
    const hasLongData = Math.max(...timeValues) > TCPMAX;
    if (!hasLongData) {
        params[3] = 5;
    }
    
    const [CP, W_prime, Pmax, A] = params;

    // Calculate predictions and residuals
    const predictions = timeValues.map(t => ompd_power(t, CP, W_prime, Pmax, A));
    const residuals = powerValues.map((p, i) => p - predictions[i]);
    const RMSE = Math.sqrt(residuals.reduce((sum, r) => sum + r * r, 0) / residuals.length);
    const MAE = residuals.reduce((sum, r) => sum + Math.abs(r), 0) / residuals.length;

    // Calculate t99 (time to reach 99% of W')
    const t_99_range = Array.from({length: 500}, (_, i) => 1 + i * (180 - 1) / 499);
    const weff_vals = t_99_range.map(t => w_eff(t, W_prime, CP, Pmax));
    const W_99 = 0.99 * W_prime;
    const t_99_idx = weff_vals.reduce((minIdx, val, idx, arr) => 
        Math.abs(val - W_99) < Math.abs(arr[minIdx] - W_99) ? idx : minIdx, 0);
    const t_99 = t_99_range[t_99_idx];

    return {
        CP: Math.round(CP),
        W_prime: Math.round(W_prime),
        Pmax: Math.round(Pmax),
        A: parseFloat(A.toFixed(2)),
        RMSE: parseFloat(RMSE.toFixed(2)),
        MAE: parseFloat(MAE.toFixed(2)),
        t_99: Math.round(t_99),
        pointsUsed: timeValues.length,
        predictions,
        residuals,
        params // Raw params for further calculations
    };
}

/**
 * CENTRALIZED CP CALCULATION FUNCTION
 * Used by athletes, teams, and categories modules
 * Change calculation logic here only - affects everywhere automatically
 * 
 * @param {Array} durations - Time values in seconds
 * @param {Array} watts - Power values in watts
 * @param {Number} weight - Athlete weight in kg (default 1)
 * @returns {Object} CP results: {cp, w_prime, pmax, rmse, cp_kg, w_prime_kg, pmax_kg, usedPercentile, pointsUsed, mmp_*, a_param, t_99}
 */
function calculateCPModel(durations, watts, weight = 1) {
    if (!durations || !watts || durations.length < 4) {
        return null;
    }
    const valuesPerWindow = 1;
    let currentPercentile = 100;  // Start from 100% and auto-search down
    let selectedTimes = [];
    let selectedPowers = [];
    let forcedLongPoint = false; // Track if fallback was used

    // Auto-search for percentile
    while (currentPercentile >= 0) {
        selectedTimes = [];
        selectedPowers = [];
        
        // Fit all data to get residuals
        const params = curveFit(durations, watts);
        const predictions = durations.map((t) => ompd_power(t, ...params));
        const residuals = watts.map((p, i) => p - predictions[i]);

        // Calculate percentile threshold
        const residualsClean = residuals.filter(r => !isNaN(r));
        if (residualsClean.length === 0) {
            currentPercentile--;
            continue;
        }

        residualsClean.sort((a, b) => a - b);
        const h = (residualsClean.length - 1) * (currentPercentile / 100);
        const floor_idx = Math.floor(h);
        const ceil_idx = Math.ceil(h);
        const frac = h - floor_idx;
        
        let percentileThreshold;
        if (floor_idx === ceil_idx) {
            percentileThreshold = residualsClean[floor_idx];
        } else {
            percentileThreshold = residualsClean[floor_idx] * (1 - frac) + residualsClean[ceil_idx] * frac;
        }

        // Define time windows: 2-minute intervals up to 30 min, then 15-minute intervals to 90 min
        const timeWindows = [];
        for (let start = 120; start < 1800; start += 120) {
            timeWindows.push([start, start + 120]);
        }
        for (let start = 1800; start < 5400; start += 900) {
            timeWindows.push([start, start + 900]);
        }

        let selectedMask = new Array(durations.length).fill(false);
        forcedLongPoint = false; // Reset for each iteration

        // Select points from each window
        for (const [tmin, tmax] of timeWindows) {
            const windowIndices = [];
            for (let i = 0; i < durations.length; i++) {
                if (durations[i] >= tmin && durations[i] <= tmax) {
                    windowIndices.push(i);
                }
            }
            if (windowIndices.length === 0) continue;

            // Sort by residual descending
            const sortedIndices = windowIndices.sort((a, b) => residuals[b] - residuals[a]);

            // Take up to valuesPerWindow where residual >= threshold
            let count = 0;
            for (const i of sortedIndices) {
                if (!isNaN(residuals[i]) && residuals[i] >= percentileThreshold && !selectedMask[i]) {
                    selectedTimes.push(durations[i]);
                    selectedPowers.push(watts[i]);
                    selectedMask[i] = true;
                    count++;
                    if (count >= valuesPerWindow) break;
                }
            }
        }

        // Sprint point (1 second)
        let minDist = Infinity;
        let sprintIdx = -1;
        for (let i = 0; i < durations.length; i++) {
            const dist = Math.abs(durations[i] - 1);
            if (dist < minDist) {
                minDist = dist;
                sprintIdx = i;
            }
        }
        if (sprintIdx >= 0 && !selectedMask[sprintIdx]) {
            selectedTimes.push(durations[sprintIdx]);
            selectedPowers.push(watts[sprintIdx]);
            selectedMask[sprintIdx] = true;
        }

        // CHECK: If no points > 600s, add best point from 10-30 min range
        const hasLongPoint = selectedTimes.some(t => t > 600);
        if (!hasLongPoint) {
            let bestIdx = -1;
            let bestResidual = -Infinity;
            
            // Find highest residual in 10-30 min range (600-1800s)
            for (let i = 0; i < durations.length; i++) {
                if (durations[i] >= 600 && durations[i] <= 1800 && !selectedMask[i]) {
                    if (residuals[i] > bestResidual) {
                        bestResidual = residuals[i];
                        bestIdx = i;
                    }
                }
            }
            
            if (bestIdx >= 0) {
                selectedTimes.push(durations[bestIdx]);
                selectedPowers.push(watts[bestIdx]);
                selectedMask[bestIdx] = true;
                
                // Calculate the percentile of this forced point
                let position = 0;
                for (let r of residualsClean) {
                    if (r < bestResidual) position++;
                }
                const forcedPointPercentile = (position / (residualsClean.length - 1)) * 100;
                forcedLongPoint = Math.round(forcedPointPercentile); // Store as percentile value
            }
        }

        // Check if we have enough points
        if (selectedTimes.length >= 4) {
            break;
        }
        
        currentPercentile--;
    }

    if (selectedTimes.length < 4) {
        return null;
    }

    // Sort selected data by time for proper plotting
    const sortedIndices = selectedTimes.map((_, i) => i).sort((a, b) => selectedTimes[a] - selectedTimes[b]);
    selectedTimes = sortedIndices.map(i => selectedTimes[i]);
    selectedPowers = sortedIndices.map(i => selectedPowers[i]);

    // Calculate final CP model with selected points
    const cpResult = calculateOmniPD(selectedTimes, selectedPowers);

    // Extract MMP for specific durations
    const targetDurations = [1, 5, 180, 360, 720]; // 1s, 5s, 3m, 6m, 12m
    const mmps = {};
    for (const duration of targetDurations) {
        const index = durations.findIndex(d => d >= duration);
        mmps[duration] = (index !== -1) ? watts[index] : null;
    }

    // Return result object
    return {
        cp: Math.round(cpResult.CP),
        w_prime: Math.round(cpResult.W_prime),
        pmax: Math.round(cpResult.Pmax),
        rmse: cpResult.RMSE.toFixed(2),
        cp_kg: (cpResult.CP / weight).toFixed(2),
        w_prime_kg: (cpResult.W_prime / weight / 1000).toFixed(3),
        pmax_kg: (cpResult.Pmax / weight).toFixed(2),
        a_param: cpResult.A,
        t_99: cpResult.t_99,
        usedPercentile: currentPercentile,
        pointsUsed: selectedTimes.length,
        forcedLongPoint: forcedLongPoint,
        mmp_1s: mmps[1],
        mmp_5s: mmps[5],
        mmp_3m: mmps[180],
        mmp_6m: mmps[360],
        mmp_12m: mmps[720]
    };
}
