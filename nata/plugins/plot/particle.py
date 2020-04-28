# -*- coding: utf-8 -*-
from typing import List
from typing import Optional

import numpy as np

from nata.containers import ParticleDataset
from nata.plots.axes import Axes
from nata.plots.data import PlotData
from nata.plots.data import PlotDataAxis
from nata.plots.figure import Figure
from nata.plots.helpers import filter_style
from nata.plots.plans import AxesPlan
from nata.plots.plans import FigurePlan
from nata.plots.plans import PlotPlan
from nata.plots.types import DefaultParticlePlotType
from nata.plugins.register import register_container_plugin
from nata.utils.env import inside_notebook


@register_container_plugin(ParticleDataset, name="plot_data")
def particle_plot_data(
    dataset: ParticleDataset, quants: List[str] = []
) -> PlotData:
    a = []
    d = []

    for quant in quants:
        q = dataset.quantities[quant]
        new_a = PlotDataAxis(name=q.name, label=q.label, units=q.unit)

        a.append(new_a)
        d.append(np.array(q))

    p_d = PlotData(
        name=dataset.name,
        label=dataset.name,
        units="",
        data=d,
        time=np.array(dataset.axes["time"]),
        time_units=dataset.axes["time"].unit,
        axes=a,
    )

    return p_d


@register_container_plugin(ParticleDataset, name="plot_type")
def particle_plot_type(dataset: ParticleDataset) -> PlotData:
    return DefaultParticlePlotType


@register_container_plugin(ParticleDataset, name="plot")
def plot_particle_dataset(
    dataset: ParticleDataset,
    quants: List[str] = [],
    fig: Optional[Figure] = None,
    axes: Optional[Axes] = None,
    style: dict = dict(),
    interactive: bool = True,
    n: int = 0,
):
    """Plots a single/multiple iteration :class:`nata.containers.ParticleDataset`\
       using a :class:`nata.plots.types.ScatterPlot`.

        Parameters
        ----------
        quants: ``list``
            List of the names of particle quantities that should be represented
            in the figure. The first two (compulsory) quantities are
            represented in the horizontal and vertical axes, respectively. The
            third quantity (optional) is represented in colors, in which case
            a colorbar is added to the figure by default.

        fig: :class:`nata.plots.Figure`, optional
            If provided, the plot is drawn on ``fig``. The plot is drawn on
            ``axes`` if it is a child axes of ``fig``, otherwise a new axes
            is created on ``fig``. If ``fig`` is not provided, a new
            :class:`nata.plots.Figure` is created.

        axes: :class:`nata.plots.Axes`, optional
            If provided, the plot is drawn on ``axes``, which must be an axes
            of ``fig``. If ``axes`` is not provided or is provided without a
            corresponding ``fig``, a new :class:`nata.plots.Axes` is created in
            a new :class:`nata.plots.Figure`.

        style: ``dict``, optional
            Dictionary that takes a mix of style properties of
            :class:`nata.plots.Figure`, :class:`nata.plots.Axes` and any plot
            type (see :class:`nata.plots.types.ScatterPlot`).

        interactive: ``bool``, optional
            Controls wether interactive widgets should be shown with the plot
            to allow for temporal navigation. Only applicable if ``dataset``
            has multiple iterations.

        n: ``int``, optional
            Selects the index of the iteration to be shown initially. Only
            applicable if ``dataset`` has multiple iterations, .

        Returns
        ------
        :class:`nata.plots.Figure` or ``None``:
            Figure with plot built based on ``dataset``. Interactive widgets
            are shown with the figure if ``dataset`` has multiple iterations,
            in which case this method returns  ``None``.

        Examples
        --------
        To get a plot with default style properties in a new figure, simply
        call the ``.plot()`` method selecting the particle quantities that
        should be shown.

        >>> from nata.containers import ParticleDataset
        >>> import numpy as np
        >>> arr = np.arange(30).reshape(1,10,3)
        >>> ds = ParticleDataset(arr, quants=["quant0", "quant1"])
        >>> fig = ds.plot()

        In case a :class:`nata.plots.Figure` is returned by the method, it can
        be shown by calling the :func:`nata.plots.Figure.show` method.

        >>> fig.show()

        To draw a new plot on ``fig``, we can pass it as an argument to the
        ``.plot()`` method. If ``axes`` is provided, the new plot is drawn on
        the selected axes. In this example we overlay a
        :class:`nata.plots.types.LinePlot` created from a
        :class:`nata.containers.GridDataset` on the
        :class:`nata.plots.types.ScatterPlot` previously created.

        >>> from nata.containers import GridDataset
        >>> arr2 = np.arange(10)
        >>> ds2 = GridDataset(arr2[np.newaxis])
        >>> ds2.plot(fig=fig, axes=fig.axes[0])

        The :func:`nata.plots.Figure._repr_html_` calls the
        :func:`nata.plots.Figure.show` method, so in a notebook
        environment the returned figure will be shown by default if ``plot()``
        is the last method called in a cell.


    """

    p_plan = PlotPlan(
        dataset=dataset,
        quants=quants,
        style=filter_style(dataset.plot_type(), style),
    )

    a_plan = AxesPlan(
        axes=axes, plots=[p_plan], style=filter_style(Axes, style)
    )

    f_plan = FigurePlan(
        fig=fig, axes=[a_plan], style=filter_style(Figure, style)
    )

    if len(dataset) > 1 and inside_notebook() and interactive:
        f_plan.build_interactive(n)

    else:
        return f_plan.build()
