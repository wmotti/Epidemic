#!/usr/bin/env python

"""A simple epidemiological model, SIR, with:
    - recover
    - temporary immunization
but
    - no death
    - no permanent immunization
    - no vital dynamics

Three possible states for an individual:
    - susceptible
    - infect
    - immune

Conditions of termination of the simulation:
    - no more infects in the population
    - time exceeds run_time
"""

from Epidemic import Epidemic

epidemic_params = dict(
    nr_individuals = 100,
    initial_infects = 10,
    initial_immunes = 0,
    infect_prob = 0.003,
    contact_rate = 1,
    recover_rate = 0.003,
    immune_after_recovery = True,
    immunization_vanish_rate = 0.001,
    run_time = 5000
)

run = Epidemic.Epidemic(epidemic_params)