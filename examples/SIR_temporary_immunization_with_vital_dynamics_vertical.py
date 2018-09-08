#!/usr/bin/env python

"""A simple epidemiological model, SIR, with:
    - recover
    - temporary immunization
    - death (by epidemic)
    - vital dynamics
    - "vertical" infection (parents transmit the infection to newborns)
    - "vertical" immunization (parents transmit the immunization to newborns)

Four possible states for an individual:
    - susceptible
    - infect
    - immune
    - dead

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
    contact_rate = 3,
    recover_rate = 0.003,
    immune_after_recovery = True,
    immunization_vanish_rate = 0.001,
    death_rate = 0.0001,
    newborn_can_be_infect = True,
    newborn_can_be_immune = True,
    newborn_prob = 0.0001,
    natural_death_prob = 0.01,
    run_time = 5000
)

run = Epidemic.Epidemic(epidemic_params)