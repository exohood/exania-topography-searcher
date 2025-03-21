""" Functions to produce a contour plot for a two-dimensional surface
    with the kinetic transition network containing minima and
    transition states overlaid onto it """

from matplotlib.colors import Colormap
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import rc
import numpy as np
from nptyping import NDArray
from topsearch.data.kinetic_transition_network import KineticTransitionNetwork

from topsearch.potentials.potential import Potential

rc('font', **{'family': 'serif'})
rc('text', usetex=False)
mpl.rcParams.update({'font.size': 18})


def plot_stationary_points(potential: Potential, ktn: KineticTransitionNetwork, bounds: list,
                           label: str = '', contour_levels: int = 50,
                           fineness: int = 50, colour_scheme: str = 'cool',
                           label_min: bool = False) -> None:
    """ Plot all minima and transition states of the function. Each transition
        state is given in red and each minimum in green with a labelling
        matching min.data. Connected minima of each transition state are
        joined by solid black lines """

    plt.figure()
    cmap = plt.get_cmap(colour_scheme, contour_levels+1)
    # Get the coordinates of all minima and their labels
    min_labels = []
    minima = np.zeros((ktn.n_minima, 2))
    for i in range(ktn.n_minima):
        minima[i, :] = ktn.get_minimum_coords(i)
        min_labels.append([minima[i, 0], minima[i, 1], i])
    # Get the function contours
    contour_set = plot_contours(potential, bounds, fineness,
                                contour_levels, cmap)
    count = 0
    # Initialise transition state array without self-connections
    selfconnected = self_connected(ktn)
    ts_coords = np.zeros((len(ktn.G.edges)-selfconnected, 2))
    # Plot the connections between minima and transition states
    for node1, node2, edge_index in ktn.G.edges:
        if node1 == node2:
            continue
        ts_coords[count, :] = ktn.get_ts_coords(node1, node2, edge_index)
        # Arrows to show connections between transition states and minima
        plt.arrow(ts_coords[count, 0], ts_coords[count, 1],
                  minima[node1, 0] - ts_coords[count, 0],
                  minima[node1, 1] - ts_coords[count, 1],
                  zorder=1)
        plt.arrow(ts_coords[count, 0], ts_coords[count, 1],
                  minima[node2, 0] - ts_coords[count, 0],
                  minima[node2, 1] - ts_coords[count, 1],
                  zorder=1)
        count += 1
    # Add the minima and transition states
    plt.scatter(ts_coords[:, 0], ts_coords[:, 1], c='r', zorder=3, s=2.0)
    plt.scatter(minima[:, 0], minima[:, 1], c='g', zorder=3, s=2.0)
    # Add the numerical labels for each minimum
    if label_min:
        for i in min_labels:
            plt.text(i[0], i[1], str(i[2]), fontsize=5)
    # Add labels and write to disc
    plt.xlabel(r'$x$')
    plt.ylabel(r'$y$')
    plt.xlim(bounds[0])
    plt.ylim(bounds[1])
    plt.colorbar(contour_set)
    plt.tight_layout()
    plt.savefig(f"StationaryPoints{label}.png", dpi=300)
    plt.cla()
    plt.clf()
    plt.close()


def self_connected(ktn: KineticTransitionNetwork) -> int:
    """ Count the number of edges that connect minima to themselves """
    selfconnected = 0
    for node1, node2 in ktn.G.edges():
        if node1 == node2:
            selfconnected += 1
    return selfconnected


def make_xy_grid(bounds: list, fineness: int) -> tuple[NDArray, NDArray]:
    """ Produce the xy grid that the function will be evaluated on
        for the contour plot """
    x_grid, y_grid = np.meshgrid(
        np.linspace(bounds[0][0], bounds[0][1], fineness),
        np.linspace(bounds[1][0], bounds[1][1], fineness))
    return x_grid, y_grid


def plot_contours(potential: Potential, bounds: list, fineness: int,
                  contour_levels: int, cmap: Colormap) -> NDArray:
    """ Make a contour plot of the potential within the range bounds """
    x_grid, y_grid = make_xy_grid(bounds, fineness)
    z_grid = compute_function_grid(potential, x_grid, y_grid, fineness)
    contour_set = plt.contour(x_grid, y_grid, z_grid,
                              contour_levels, cmap=cmap, zorder=-1)
    return contour_set


def compute_function_grid(potential: Potential, x_array: NDArray,
                          y_array: NDArray, fineness: int) -> NDArray:
    """ Returns the function value evaluated for the grid of
        meshgrid input for plotting """
    z_array = []
    for i in map(lambda x: function_call(potential, x),
                 zip(x_array.flatten(), y_array.flatten())):
        z_array.append(i)
    return np.asarray(z_array).reshape((fineness, fineness))


def function_call(potential: Potential, x_value: NDArray) -> float:
    """ Returns function value """
    x_tmp = np.array(x_value)
    return potential.function(x_tmp)
