#!/usr/bin/env python
# -*- coding: iso8859-1 -*-

"""Epidemic module, useful to simulate an epidemic spreading in a population."""

from __future__ import division

import os
import random
import sys
import time

# Use Psyco if available
try:
    import psyco
    psyco.full()
    # psyco.log('Epidemic-psyco.log')
except ImportError:
    print "warning: the psyco module cannot be found. The simulation will run anyway, maybe slower."
    pass

try:
    from SimPy.Simulation import Monitor, Process, stopSimulation, activate, \
                                 passivate, simulate, initialize, hold, now
except ImportError:
    print "error: the SimPy.Simulation package cannot be found. Install SimPy and try again."

class Epidemic:
    """A class for modelling and simulating epidemics."""

    def __init__(self, epidemic_params):
        """The constructor of the class.
           Full params' list:
            - nr_individuals: number of individuals in the population
            - initial_infects: number of infects at the start of the simulation
            - initial_immunes: number of immunes at the start of the simulation
            - infect_prob: probability of getting infected after a contact with an infect
            - contact_rate: rate of the contact between individuals
            - recover_rate: rate of recover from infection
            - immune_after_recovery: if true, individuals becomes immunes after recovery
            - immunization_vanish_rate: if not zero, immunization is temporary with given rate
            - death_rate: rate of death caused by epidemic
            - newborn_can_be_infect: if true, newborn can be infect
            - newborn_can_be_immune: if true, newborn can be immune
            - newborn_prob: probability that a new individual born after a contact
            - natural_death_prob: probability of death not caused by epidemic
            - run_time: time duration of the simulation
            - debug: show more info about the running simulation
            - process_debug: show more info about SimPy processes during the simulation
            - progress: show a progress indicator during the simulation
            - stats: show some stats at the end of the simulation
            - plot: show a plot representing the evolution of the population at the end of the simulation
        """
        # setting up the epidemic's parameters with metaprogramming
        for param in epidemic_params:
            self.__dict__[param] = epidemic_params.get(param)
        # setting the uninitialized parameters to their default values
        self.check_and_set_default_value(['initial_immunes', 'recover_rate', 'death_rate', 'immunization_vanish_rate', 'newborn_prob', 'natural_death_prob'], ['immune_after_recovery', 'newborn_can_be_immune', 'newborn_can_be_infect', 'debug', 'process_debug', 'progress', 'stats', 'plot'])
        # setting the random number generator using the python standard one
        self.rng = random.Random()
        # checking some features of the model from parameters passed to the constructor
        self.model_has_immunization = self.model_has_immunization()
        self.model_immunization_is_permanent = self.model_immunization_is_permanent()
        self.model_has_recovering = self.model_has_recovering()
        self.model_has_death = self.model_has_death()
        self.model_has_vital_dynamics = self.model_has_vital_dynamics()
        self.model_newborns_always_susceptibles = self.model_newborns_always_susceptibles()
        self.model_has_new_susceptibles = self.model_has_new_susceptibles()
        self.model_has_new_infects = self.model_has_new_infects()
        # initialize the population counters
        self.total_infects = self.initial_infects
        self.total_immunes = self.initial_immunes
        self.total_susceptibles = self.nr_individuals - self.initial_infects - self.initial_immunes
        self.total_newborns = 0
        self.total_natural_deaths = 0
        self.total_deaths = 0
        # setting up the monitors for watching interesting variables
        self.m_suscettibili = Monitor(name="Suscettibili", ylab="suscettibili")
        self.m_suscettibili.append([0, self.total_susceptibles])
        self.m_infetti = Monitor(name="Infetti", ylab='infetti')
        self.m_infetti.append([0, self.initial_infects])
        if self.model_has_immunization:
            self.m_immuni = Monitor(name="Immuni", ylab='immuni')
            self.m_immuni.append([0, self.initial_immunes])
        # setting up the array of all the individuals partecipating to the simulation
        self.all_individuals = []
        # initialize the simulation environment (time, events, ...)
        initialize()
        for i in range(self.nr_individuals):
            # add individuals to the simulation with the specified health_status
            if i >= (self.nr_individuals - self.initial_infects):
                ind = self.Individual(self, ind_id=i, health_status='infect')
            elif i >= (self.nr_individuals - self.initial_infects -
                    self.initial_immunes):
                ind = self.Individual(self, ind_id=i, health_status='immune')
            else:
                ind = self.Individual(self, ind_id=i)
            # activate it with function live()
            activate(ind, ind.live(), at=0.0)
        self.start_time = time.time()
        if self.process_debug:
            self.show_processes_status()
        # start the simulation
        simulate(until=self.run_time)
        self.stop_time = time.time()
        if self.process_debug:
            self.show_processes_status()
        # show final stats if required by params
        if self.stats:
            self.show_stats()
        # show plot if required by params
        if self.plot:
            self.show_plot()

    def model_has_recovering(self):
        """Checks from parameters if the epidemiological model has recovering."""
        if self.recover_rate:
            return True
        else:
            return False

    def model_has_immunization(self):
        """Checks from parameters if the epidemiological model has immunization."""
        if (self.model_has_recovering and self.immune_after_recovery) or (self.newborn_prob and self.newborn_can_be_immune):
            return True
        else:
            return False

    def model_immunization_is_permanent(self):
        """Checks from parameters if the epidemiological model has permanent immunization."""
        if self.model_has_immunization and self.immunization_vanish_rate == 0:
            return True
        else:
            return False

    def model_has_death(self):
        """Checks from parameters if the epidemiological model has death."""
        if self.death_rate:
            return True
        else:
            return False

    def model_has_vital_dynamics(self):
        """Checks from parameters if the epidemiological model has vital dynamics (births and natural deaths)."""
        if (self.newborn_prob or self.natural_death_prob):
            return True
        else:
            return False

    def model_has_new_susceptibles(self):
        """Checks if the number of the susceptibles can increase during the simulation."""
        if self.model_has_recovering or \
          (self.model_has_immunization and not self.model_immunization_is_permanent) or \
           self.model_has_vital_dynamics:
            return True
        else:
            return False

    def model_has_new_infects(self):
        """Checks if the number of the infects can increase during the simulation, but not for susceptibles getting infected."""
        if self.model_has_vital_dynamics and not self.model_newborns_always_susceptibles:
            return True
        else:
            return False

    def model_newborns_always_susceptibles(self):
        """Checks if newborns are always susceptibles in the epidemiological model."""
        if self.model_has_vital_dynamics and not (self.newborn_can_be_immune and self.newborn_can_be_infect):
            return True
        else:
            return False

    def check_and_set_default_value(self, num_params, bool_params):
        """Checks if some optional parameters are set and, if not, set them to their default values.
        The default values of the optional parameters are:
        - 0 for every numerical parameters;
        - True for parameters "progress", "plot", "stats"
        - False for every other boolean parameters

        Input: two dictionaries of optional parameters of the constructor of the class
        Output: none (but the optional parameters are setted with their default values)
        """
        for param in num_params:
            if hasattr(self, param) == False:
                self.__dict__[param] = 0
        for param in bool_params:
            if hasattr(self, param) == False:
                if param in ['progress', 'plot', 'stats']:
                    self.__dict__[param] = True
                else:
                    self.__dict__[param] = False

    def show_processes_status(self):
        """Returns the current internal status of the simulation processes."""
        active_counter = 0
        passive_counter = 0
        terminated_counter = 0
        interrupted_counter = 0
        for ind in self.all_individuals:
            if ind.active():
                active_counter += 1
            if ind.passive():
                passive_counter += 1
            if ind.terminated():
                terminated_counter += 1
            if ind.interrupted():
                interrupted_counter += 1
        print "Processes' status: %3i active, %3i passive, %3i terminated, %3i interrupted" % (active_counter, passive_counter, terminated_counter, interrupted_counter)

    def wait(self, rate):
        '''Returns the time interval before the next event.'''
        return self.rng.expovariate(rate)

    def next_event(self, events_rates):
        """Returns the next event, choosen from the given ones, and the time interval before it.

        Input: a dictionary of possible events and their respective rates
        Output: one of the possible events passed as input, and the time interval before it.
        """
        rnd = self.rng.random()
        total_rates = 0
        for event in events_rates:
            total_rates += events_rates.get(event)
        cumulated_rates = 0
        for event in events_rates:
            cumulated_rates += events_rates.get(event)
            if rnd <= cumulated_rates/total_rates:
                returned_event = event
                break
        returned_event_interval = self.wait(total_rates)
        return returned_event, returned_event_interval

    def observe_vars(self):
        """Watches and records the values of the monitored variables."""
        self.m_infetti.observe(self.total_infects)
        self.m_suscettibili.observe(self.total_susceptibles)
        if self.model_has_immunization:
            self.m_immuni.observe(self.total_immunes)

    def check_termination_conds(self):
        """Checks particular situations in which the simulation can be stopped before the time runs out."""
        if self.total_infects == 0:
            if self.debug:
                print "[%f] STOP: infection ended, no more infects!"% (now())
            print "\nSimulation ended prematurely: infection ended, no more infects."
            return True
        if not self.model_has_new_susceptibles:
            if self.total_susceptibles == 0 and self.total_immunes == 0:
                if self.debug:
                    print "[%f] STOP: infection extended to the whole population!"% (now())
                print "\nSimulation ended prematurely: infection extended to the whole population."
                return True
        if self.model_immunization_is_permanent and not self.model_has_vital_dynamics:
            if self.total_susceptibles == 0 and self.total_immunes == 0:
                if self.debug:
                    print "[%f] STOP: infection ended, permanent immunizzation extended to the whole population!"% (now())
                print "\nSimulation ended prematurely: infection ended, permanent immunizzation extended to the whole population."
                return True
        return False

    def check_current_nr_individuals(self):
        """Checks the correct number of individuals during the simulation."""
        assert self.nr_individuals + self.total_newborns - self.total_natural_deaths - self.total_deaths == self.total_susceptibles + self.total_infects + self.total_immunes, "error: assert failed on the current number of individuals."

    def stop_simulation(self):
        """Stops the simulation."""
        stopSimulation()

    def show_plot(self):
        """Plots the number of infected, susceptibles and, eventually, immunes against time using gnuplot-py."""
        try:
            import Gnuplot
        except ImportError:
            print "warning: the gnuplot-py module cannot be found. The simulation will run anyway, but you could not plot the graph."
            pass
        g = Gnuplot.Gnuplot()
        if os.getenv('DISPLAY') == None:
	    g('set term png')
            g('set output "test.png"')
	else:
	    g('persist=1')
        g.xlabel('t')
        g.ylabel('number of individuals')
        x_infetti = self.m_infetti.tseries()
        y_infetti = self.m_infetti.yseries()
        x_suscettibili = self.m_suscettibili.tseries()
        y_suscettibili = self.m_suscettibili.yseries()
        g_infetti = Gnuplot.Data(x_infetti, y_infetti, inline=True, title='Infects', with='steps 1')
        g_suscettibili = Gnuplot.Data(x_suscettibili, y_suscettibili, inline=True, title='Susceptibles', with='steps 2')
        if self.model_has_immunization:
            x_immuni = self.m_immuni.tseries()
            y_immuni = self.m_immuni.yseries()
            g_immuni = Gnuplot.Data(x_immuni, y_immuni, inline=True, title='Immunes', with='steps 3')
            g.plot(g_infetti, g_suscettibili, g_immuni)
            g.title('Graph of susceptibles, infects and immunes against time')
        else:
            g.plot(g_infetti, g_suscettibili)
            g.title('Graph of susceptibles, infects against time')
        # other possible graph types:
        # with='steps'
        # with='lines'
        # with='lp 1 2', where 1 is the color and 2 is the marks' type

    def show_stats(self):
        """Prints some data about the epidemic's simulation."""
        print "\nSimulation duration: %f seconds"% (
                                            self.stop_time-self.start_time)
        print "Situation at the end of the simulation:"
        print "- infects: %i"% (self.total_infects)
        print "- susceptibles: %i"% (self.total_susceptibles)
        if self.model_has_immunization:
            print "- immunes: %i"% (self.total_immunes)
        if self.model_has_death:
            print "- deaths for the epidemic: %i"% (self.total_deaths)
        if self.model_has_vital_dynamics:
            print "- births: %i"% (self.total_newborns)
            print "- deaths for natural reasons: %i"% (self.total_natural_deaths)

    def show_progress(self):
        """Shows a progress indicator during the run of the simulation."""
        if self.progress:
            progress = now() / self.run_time * 100
            sys.stdout.write("\b\b\b\b\b\b")
            sys.stdout.write("%5.2f%%" % (progress))
            sys.stdout.flush()

    def add_an_individual(self, health_status):
        """Adds a newborn individual to the simulation."""
        self.total_newborns += 1
        ind = self.Individual(self, ind_id= self.nr_individuals + self.total_newborns, health_status = health_status)
        self.__dict__['total_' + health_status + 's'] += 1
        self.observe_vars()
        activate(ind, ind.live(), at=0.0)

    def print_debug(self, func):
        """Prints a debug line about the population's status."""
        if self.debug == True:
            print "[%7.2f] %-15s: %3i susceptibles, %3i infects, %3i immunes, %3i deaths (%3i births, %3i natural deaths)"% (now(), func, self.total_susceptibles, self.total_infects, self.total_immunes, self.total_deaths, self.total_newborns, self.total_natural_deaths)

    class Individual(Process):
        """An individual in a population, either susceptible, infect or immune."""
        __slots__ = 'ind_id', 'epidemic', 'health_status'
        def __init__(self, epidemic, ind_id, health_status='susceptible'):
            Process.__init__(self)
            self.ind_id = ind_id
            self.e = epidemic
            self.health_status = health_status
            self.e.all_individuals.append(self)

        def choose_contact(self):
            """Returns the individual of the next contact."""
            contact = self
            while contact == self:
                contact = self.e.rng.choice(self.e.all_individuals)
            return contact

        def get_infect(self):
            """The individual becomes infect."""
            self.health_status = 'infect'
            self.e.total_infects += 1
            self.e.total_susceptibles -= 1
            self.e.check_current_nr_individuals()
            self.e.observe_vars()
            self.e.print_debug('get_infect')
            self.e.show_progress()
            if self.e.check_termination_conds():
                self.e.stop_simulation()

        def get_immune(self):
            """The individual becomes immune."""
            self.health_status = 'immune'
            self.e.total_immunes += 1
            self.e.total_infects -= 1
            self.e.check_current_nr_individuals()
            self.e.observe_vars()
            self.e.print_debug('get_immune')
            self.e.show_progress()
            if self.e.check_termination_conds():
                self.e.stop_simulation()

        def get_susceptible(self):
            """The individual becomes susceptible."""
            self.health_status = 'susceptible'
            self.e.total_susceptibles += 1
            if self.e.immune_after_recovery == False:
                self.e.total_infects -= 1
            elif self.e.immunization_vanish_rate != 0:
                self.e.total_immunes -= 1
            self.e.check_current_nr_individuals()
            self.e.observe_vars()
            self.e.print_debug('get_susceptible')
            self.e.show_progress()
            if self.e.check_termination_conds():
                self.e.stop_simulation()

        def get_in_contact(self):
            """The individual get in contact with another individual."""
            contact = self.choose_contact()
            # infection?
            if self.e.rng.random() <= self.e.infect_prob:
                if self.health_status == 'susceptible' and contact.health_status == 'infect':
                    if self.e.debug:
                        print "I was %s, now I've been infected by a %s!" % (self.health_status, contact.health_status)
                    self.get_infect()
                elif self.health_status == 'infect' and contact.health_status == 'susceptible':
                    if self.e.debug:
                        print "The individual #%i, %s, now infects the individual #%i, %s." % (self.ind_id, self.health_status, contact.ind_id, contact.health_status)
                    contact.get_infect()
            # birth of a child?
            # the contact between a man and a woman will happen in one case out of two
            if self.e.newborn_prob != 0 and self.e.rng.random() <= 0.5 and \
               self.e.rng.random() <= self.e.newborn_prob:
                if self.e.newborn_can_be_infect == True and \
                  ((self.health_status == 'infect' and contact.health_status != 'immune') or \
                   (contact.health_status == 'infect' and self.health_status != 'immune')):
                    newborn_health_status = 'infect'
                # The mother will be the immune parent only in one case out of two.
                # Then, only in these cases the newborn will receive "vertically" the immunity
                if self.e.newborn_can_be_immune == True and self.e.rng.random() <= 0.5 and \
                   (self.health_status == 'immune' or contact.health_status == 'immune'):
                    newborn_health_status = 'immune'
                else:
                    newborn_health_status = 'susceptible'
                self.e.add_an_individual(newborn_health_status)

        def die(self, naturally=True):
            """An individual dies, for natural reasons or for the epidemic."""
            if naturally == True:
                self.e.total_natural_deaths += 1
            else:
                self.e.total_deaths += 1
            self.e.__dict__['total_' + self.health_status + 's'] -= 1
            self.e.observe_vars()
            self.e.all_individuals.remove(self)
            self.e.print_debug('die')

        def live(self):
            """Method that defines the life cycle of the individual.
            This is the Process Execution Method (PEM) of the SimPy process."""

            while 1:
                # considering the natural death probability
                if self.e.natural_death_prob:
                    if self.e.rng.random() <= self.e.natural_death_prob:
                        self.die(naturally=True)
                        yield passivate, self

                # life cycle of a susceptible individual
                while self.health_status == 'susceptible':
                    wait = self.e.wait(self.e.contact_rate)
                    yield hold, self, wait
                    self.get_in_contact()

                # life cycle of an infect individual
                while self.health_status == 'infect':
                    event, wait = self.e.next_event(dict(
                        contact = self.e.contact_rate,
                        recover = self.e.recover_rate,
                        death = self.e.death_rate))
                    yield hold, self, wait
                    if event == 'recover':
                        if self.e.immune_after_recovery == True:
                            self.get_immune()
                        else:
                            self.get_susceptible()
                    elif event == 'contact':
                        self.get_in_contact()
                    elif event == 'death':
                        self.die(naturally=False)
                        yield passivate, self

                # life cycle of an immune individual
                while self.health_status == 'immune':
                    if self.e.immunization_vanish_rate != 0:
                        wait = self.e.wait(self.e.immunization_vanish_rate)
                        yield hold, self, wait
                        self.get_susceptible()
                    else:
                        yield passivate, self

if __name__ == "__main__":
    print """error: you are directly running a package, and this is not the intended way to use Epidemic.
Please look at the examples to see how you can simulate an epidemic with specified parameters."""
