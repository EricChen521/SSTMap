import numpy as np
from scipy import stats
import matplotlib as mpl
from matplotlib import cm
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from optparse import OptionParser
import seaborn as sns
sns.set_style("white")
import os
from mpl_toolkits.mplot3d import Axes3D


from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter

def getHSData(hsa_data_file):
    '''
    Returns a dictionary with hydration site index as keys and a list of various attributes as values.
    '''
    f = open(hsa_data_file, 'r')
    data = f.readlines()
    hsa_header = data[0]
    data_keys = hsa_header.strip("\n").split()
    hsa_data = {}
    for l in data[1:]:
        float_converted_data = [float(x) for x in l.strip("\n").split()[1:27]]
        hsa_data[int(l.strip("\n").split()[0])] = float_converted_data
    return hsa_data

def plotRTheta(theta_file, r_file, legend_label, nwat):
    ############################################################################################################
    integ_counts = 16.3624445886
    #integ_counts = 22560
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    theta_data = np.loadtxt(theta_file)
    r_data = np.loadtxt(r_file)
    Nnbr = len(r_data)/nwat
    print nwat, Nnbr
    # generate index matrices
    X, Y = np.mgrid[0:130:131j, 2.0:5.0:31j]
    # generate kernel density estimates
    values = np.vstack([theta_data, r_data])
    kernel =  stats.gaussian_kde(values)
    positions = np.vstack([X.ravel(), Y.ravel()])
    Z = np.reshape(kernel(positions).T, X.shape)
    Z *= integ_counts*0.1
    #Z /= integ_counts
    sum_counts_kernel = 0
    #print kernel.n
    # correct Z
    for i in xrange(0, Y.shape[1]):
        d = Y[0,i]
        # get shell_vol
        d_low = d - 0.1
        vol = (4.0/3.0)*np.pi*(d**3)
        vol_low = (4.0/3.0)*np.pi*(d_low**3)
        shell_vol =  vol - vol_low

        counts_bulk = 0.0329*shell_vol
        sum_counts_kernel += np.sum(Z[:,i])
        #Z[:,i] /= counts_bulk
        Z[:,i] = Z[:,i]/counts_bulk

    print sum_counts_kernel
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0.5, antialiased=True, alpha=1.0, cmap=cm.coolwarm, label=legend_label)
    x_label = r"$\theta^\circ$"
    y_label = r"$r (\AA)$"
    ax.set_xlabel(x_label)
    ax.set_xlim(0, 130)
    ax.set_ylabel(y_label)
    ax.set_ylim(2.0, 5.0)
    z_label = r'$\mathrm{P(\theta, \AA)}$'
    ax.set_zlabel(z_label)
    ax.legend(legend_label, loc='upper left', prop={'size':6})
    ax.set_zlim(0.0, 0.15)
    plt.savefig(legend_label + ".png", dpi=300)
    plt.close()
    ############################################################################################################



if (__name__ == '__main__') :

    _version = "$Revision: 0.0 $"
    # breakdown cases - hydrophobic
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-d", "--data_directory", dest="data_dir", type="string", help="Directory containing Enbr data")
    parser.add_option("-n", "--system_prefix", dest="prefix", type="string", help="System name")
    parser.add_option("-c", "--cluster_center", dest="clusters", type="string", help="Directory containing Enbr data")
    (options, args) = parser.parse_args()
    #print options.data_dir, os.listdir(options.data_dir)

    f = open("../indices.txt", "r")
    lines = f.readlines()
    list_dict = {}
    for l in lines:
        prot_hs_pair = l.strip("\n\t").split("\t")
        if prot_hs_pair[0] in list_dict.keys():
            #print prot_hs_pair
            list_dict[prot_hs_pair[0]].append(int(prot_hs_pair[1]))
        else:
            list_dict[prot_hs_pair[0]] = [int(prot_hs_pair[1])]

    for k in list_dict.keys():
        dir_path_hsa_summary = "../../../../raw_data/"+k+"/hsa_energy_calcs/"+k+"_hsa_ene_summary.txt"
        dir_path_clust_data = "../../../../raw_data/"+k+"/r_theta_data/"+k+"_cluster_hb_data/"
        hsa_dict = getHSData(dir_path_hsa_summary)
        for hs in list_dict[k]:
            clust_number = "%03d" % (hs)
            theta_file = dir_path_clust_data + clust_number + "_" + k + "_HBangleww"
            r_file = dir_path_clust_data + clust_number + "_" + k + "_Nbrdist"
            #print theta_file
            #print r_file
            label = k + " " + str(hs)
            label = label.title()
            print "plotting P(r, theta) distribution from: ", label
            
            plotRTheta(theta_file, r_file, label, hsa_dict[hs][3])
        
