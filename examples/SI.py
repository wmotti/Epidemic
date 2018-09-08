#!/usr/bin/env python

"""A simple epidemiological model, SI, with:
    - no death
    - no recover
    - no immunization
    - no vital dynamics

Only two possible states for an individual:
    - susceptible
    - infect

Conditions of termination of the simulation:
    - no more susceptibles in the population
    - no more infects in the population
    - time exceeds run_time
"""

from Epidemic import Epidemic

epidemic_params = dict(
    nr_individuals = 100,
    initial_infects = 10,
    infect_prob = 0.003,
    contact_rate = 3,
    run_time = 1000
)

run = Epidemic.Epidemic(epidemic_params)
