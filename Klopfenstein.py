from cmath import acosh, cos, cosh, exp, log, pi, sqrt
from math import ceil
import numpy as np
import scipy.special as special
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import csv

# Constants
C = 299792458  # Speed of light in m/s

# Inputs
fLow = 140e9  # Lowest frequency taper needs to work at (100 GHz)
fHigh = 180e9  # Highest frequency taper needs to work at (180 GHz)
fHighEff = 2 * fHigh  # Sampling frequency margin due to 'lobe' (double the highest frequency)
startFreq = 10e9  # Starting frequency for analysis/plot (10 GHz)
freqStep = 1e9  # Frequency step for analysis/plot (1 GHz)
stopFreq = 200e9  # Highest frequency for analysis/plot (200 GHz)
er = 1  # Relative permittivity
ZS = 50  # Source impedance (Ohms)
ZL = 11.9  # Load impedance (Ohms)
MaxRL = -20  # Maximum reflection loss (dB)

# Calculations
GammaMax = 10**(MaxRL / 20)  # Maximum reflection coefficient
rho0 = log(ZL / ZS) / 2
A = acosh(rho0 / GammaMax).real
wavelength = C / fLow
lambdaeff = wavelength / sqrt(er)
beta = 2 * pi / lambdaeff.real
L = (A / beta).real  # Taper length in meters

L = L * 1e6  # Convert to micrometers

# Correct calculation of number of sections
section_length = (C / fHighEff / sqrt(er) / 2 * 1e6).real  # Section length in micrometers
numSections = ceil(L / section_length)  # Number of sections in the taper
print("# of sections: %g\n" % numSections)
print("L = %g µm\n" % L)
print("L = %g mils\n" % (L / 25.4))

l = L / numSections
x = np.linspace(0 + l / 2, L - l / 2, numSections)

def integrand(y):
    return special.iv(1, A * sqrt(1 - y**2)) / (A * sqrt(1 - y**2))

def phi(x):
    results, err = integrate.quad(integrand, 0, (2 * x / L - 1).real, epsrel=1e-16)
    return results

Z = np.zeros(numSections)
for i in range(numSections):
    Z[i] = (exp(log(ZL * ZS) / 2 + rho0 * A**2 * phi(x[i]) / cosh(A))).real

print(Z)

# Export the impedance profile to a CSV file
with open(r'C:\Users\shokoohn\Desktop\Internship Docs\impedance_profile.csv', 'w', newline='') as csvfile:
    fieldnames = ['Position (µm)', 'Impedance (Ohms)']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i in range(numSections):
        writer.writerow({'Position (µm)': x[i], 'Impedance (Ohms)': Z[i]})

# Plot the impedance profile
plt.plot(x, Z)
plt.xlabel('Position (µm)')
plt.ylabel('Impedance (Ohms)')
plt.title('Impedance Profile')
plt.show()
