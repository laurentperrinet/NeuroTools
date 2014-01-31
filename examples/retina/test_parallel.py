#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
test_parallel.py
================

Trying to task farming parameter exploration

99% inspired by parameter_search_example.py from  Michael Schmuker

To run this script, you first have to invoke an IPython controller and 
computation engines. If IPython is installed correctly and with parallel 
computation support, you can just type:

> ipcluster -n 2 &

This will start two computation engines and a controller in the background.

When the controller is up, run this script:

> python parameter_search_example.py

Calculation will start, and after a few seconds (depending on your hardware) 
it will save a png graphics file that illustrates the firing rate of a neuron 
as a function of the input rate and the weight of the synapse to your current 
directory.


Laurent Perrinet, INCM, CNRS

$ Id $


"""

def model_network(param_dict):
    """
    This model network consists of a spike source and a neuron (IF_curr_alpha). 
    The spike rate of the source and the weight can be specified in the 
    param_dict. Returns the number of spikes fired during 1000 ms of simulation.
    
    Parameters:
    param_dict - dictionary with keys
                 rate - the rate of the spike source (spikes/second)
                 weight - weight of the connection source -> neuron
                 
    Returns:
    dictionary with keys:
        source_rate - the rate of the spike source
        weight - weight of the connection source -> neuron
        neuron_rate - spike rate of the neuron
    """ 
    #set up the network
    from retina import Retina
    retina = Retina(param_dict['N'])
    params = retina.params
    params.update(param_dict) # updates what changed in the dictionary
    # simulate the experiment and get its data
    data = retina.run(params)#,verbose=False)
    neuron_rate = data['out_ON_DATA'].mean_rate()
    print neuron_rate
    # return everything, including the input parameters
    return {'snr':param_dict['snr'], 
            'kernelseed':param_dict['kernelseed'], 
            'neuron_rate': neuron_rate}

    
def make_param_dict_list(N):
    """
    create a list of parameter dictionaries for the model network.
    """
    N_snr, N_seeds =  5, 10
    from NeuroTools.parameters import ParameterSpace, ParameterRange
    import numpy
    params =  ParameterSpace({
                    'N' : N,
                    'snr' : ParameterRange(list(numpy.linspace(0.1,2.0,N_snr))),
                    'kernelseed' : ParameterRange(list([12345+ k for k in range(N_seeds)]))})

    dictlist = [p.as_dict() for p in params.iter_inner()]
    return dictlist

def show_results(result):
    """
    visualizes the result of the parameter search.
    Parameters:
    result - list of result dictionaries.
    """
    import numpy
    t_smooth = 100. # ms.  integration time to show fiber activity
    snrs = numpy.sort([r['snr'] for r in result])
    neuron_rates = numpy.zeros(len(snr))
    for snr_i in range(len(snrs)):
            neuron_rates[r_i] = [r['neuron_rate'] for r in result 
                                      if (r['source_rate'] == snrs[snr_i])][0]
                                    
    import NeuroTools.plotting as plotting
    pylab = plotting.get_display(True)
    pylab.rcParams.update(plotting.pylab_params())
    print rates, neuron_rates
    subplot = pylab.imshow( neuron_rates, 
                            interpolation = 'nearest',   
                            origin = 'lower')
    plotting.set_labels(subplot.get_axes(), 
                        xlabel = 'rate',  
                        ylabel = 'weight')
    pylab.colorbar()
    # could add fancy xticks and yticks here
    import tempfile, os
    (fd,  figfilename) = tempfile.mkstemp(prefix = 'parameter_search_result', 
                                          suffix = '.png', 
                                          dir = os.getcwd())
    pylab.gcf().savefig(figfilename)
 
def run_it(N):
    """"
    Run the parameter search.
    """

    import sys
    sys.path.append('../parameter_search/')

    import parameter_search as ps
    # search the parameter space around the operating point
    param_dict_list = make_param_dict_list(N)
    srchr = ps.IPythonParameterSearcher(
        dictlist = param_dict_list,
        func = model_network)
    srchr.search()
    outlist = srchr.harvest()

    #return the results
    return outlist

if __name__ == '__main__':
    
    results = run_it(N=100)
    show_results(results)
