def laplace_mechanism(data, sensitivity, epsilon):
    """
    Add Laplace noise to an array of integers.

    Parameters:
    - data: Array of integers to which noise will be added.
    - sensitivity: Sensitivity of the query or data.
    - epsilon: Privacy parameter for differential privacy.

    Returns:
    - Noisy array of integers.
    """
    scale_parameter = sensitivity / epsilon
    laplace_noise = np.random.laplace(0, scale_parameter, len(data))
    for i in range(len(laplace_noise)):
        if (laplace_noise[i] < 0):
            laplace_noise[i] = -1 * laplace_noise[i]
    noisy_data = data + laplace_noise
    return noisy_data