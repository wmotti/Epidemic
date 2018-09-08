from distutils.core import setup

setup(
    version="0.1",
    author="Walter Mottinelli",
    author_email="wmotti@gmail.com",
    description="Epidemic, an epidemic simulator",
    long_description=\
"""Epidemic is an epidemic simulator that uses the SimPy simulation framework.

With Epidemic, it's possible to monitor the evolution of an epidemic in a population. Many epidemiological models can be simulated:
- with or without recovering;
- with or without immunization;
- with immunization after recovery or "vertical" immunization (from parents);
- with permanent or temporary immunization;
- with vital dynamics (births and natural deaths).
It's possible to set
- the initial number of individuals, infected and immunes;
- the probability of being infected, dying naturally and borning;
- the rates of many events: contact, recover, death, immunization vanishing;
- the duration of the simulation.
At the end, it's possible to print some statistics about the simulation and the resulting population, and plot the evolution of susceptibles, infects and immunes against time.""",
    license="GNU GPL",
    name="Epidemic",
    keywords=["simulation","epidemic"],
    packages=["Epidemic"],
    requires=["SimPy"]
)