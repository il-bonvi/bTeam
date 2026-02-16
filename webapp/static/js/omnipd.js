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

    // Calculate percentile threshold
    const residualsClean = residuals.filter(r => !isNaN(r));
    let percentileThreshold = -Infinity;
    if (residualsClean.length > 0) {
        residualsClean.sort((a, b) => a - b);
        const rank = Math.ceil((minPercentile / 100) * residualsClean.length) - 1;
        const idx = Math.max(0, Math.min(residualsClean.length - 1, rank));
        percentileThreshold = residualsClean[idx];
        if (isNaN(percentileThreshold)) {
            percentileThreshold = Math.min(...residualsClean);
        }
    }

    // Define time windows
    const timeWindows = [
        [120, 240],
        [240, 480],
        [480, 900],
        [900, 1800],
        [1800, 2700]
    ];

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
