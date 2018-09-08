#!/usr/bin/env python

"""A simple epidemiological model, SIS, with:
    - recover
but
    - no death
    - no immunization
    - no vital dynamics

Only two possible states for an individual:
    - susceptible
    - infect
No immunes: recovering is possible, but recovered individuals become immediately susceptible.

Conditions of termination of the simulation:
    - no more infects in the population
    - time exceeds run_time
"""

from Epidemic import Epidemic

epidemic_params = dict(
    nr_individuals = 100,
    initial_infects = 10,
    infect_prob = 0.002,
    contact_rate = 1,
    recover_rate = 0.003,
    run_time = 5000
)

run = Epidemic.Epidemic(epidemic_params)