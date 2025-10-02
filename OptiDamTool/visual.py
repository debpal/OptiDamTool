import matplotlib
import matplotlib.lines
import matplotlib.pyplot
import pandas
import geopandas
import numpy
import os
import typing
from . import utility


class Visual:

    '''
    Provides utilities for visualizing data.
    '''

    def _validate_figure_ext(
        self,
        figure_file: str
    ) -> None:
        '''
        Validate the extension of give figure file.
        '''

        # figure plot
        figure = matplotlib.pyplot.figure(
            figsize=(1, 1)
        )

        # check figure file extension
        fig_ext = os.path.splitext(figure_file)[-1][1:]
        if fig_ext not in list(figure.canvas.get_supported_filetypes().keys()):
            raise TypeError(
                f'Input figure_file extension ".{fig_ext}" is not supported for saving the figure'
            )

        matplotlib.pyplot.close(figure)

        return None

    def sediment_inflow_to_stream(
        self,
        stream_file: str,
        figure_file: str,
        fig_width: int | float = 10,
        fig_height: int | float = 5,
        sed_title: str = 'Sediment inflow (%)',
        cumsed_title: str = 'Cumulative sediment inflow (%)',
        stream_linewidth: int | float = 1,
        sed_colormap: str = 'tab20',
        cumsed_colormap: str = 'Accent',
        sed_tickgap: int | float = 1,
        cumsed_tickgap: int = 20,
        tick_fontsize: int = 12,
        title_fontsize: int = 12,
        gui_window: bool = True
    ) -> matplotlib.figure.Figure:

        '''
        Generates a figure with two horizontally arranged plots:

        - Sediment inflow percentage to individual stream segments.
        - Cumulative sediment inflow percentage to each stream segment, including all upstream connected segments.

        Both plots are normalized by the total sediment input across all stream segments.

        Parameters
        ----------
        stream_file : str
            Path to the input stream vector file, created by :meth:`OptiDamTool.Analysis.sediment_delivery_to_stream_geojson`

        figure_file : str
            Path to the output figure file.

        fig_width : float, optional
            Width of the figure in inches. Default is 10.

        fig_height : float, optional
            Height of the figure in inches. Default is 5.

        sed_title : str, optional
            Title of the suplot for sediment inflow percentage.
            Default is 'Sediment inflow (%)'.

        cumsed_title : str, optional
            Title of the suplot for cumulative sediment inflow percentage.
            Default is 'Cumulative sediment inflow (%)'.

        stream_linewidth : float, optional
            Line width for plotting the stream. Default is 1.

        sed_colormap : str, optional
            Name of the `colormap <https://matplotlib.org/stable/users/explain/colors/colormaps.html>`_
            used to generate colors for sediment percentage. Default is 'tab20'.

        sumsed_colormap : str, optional
            Name of the colormap used to generate colors for cumulative sediment percentage.
            Default is 'winter'.

        sed_tickgap : float, optional
            Gap between two y-axis ticks on the sediment inflow percentage colorbar. Default is 1.

        cumsed_tickgap : int, optional
            Gap between two y-axis ticks on cumulative sediment inflow percentage colorbar. Default is 20.

        tick_fontsize : int, optional
            Font size of the y-axis tick labels on both colorbars. Default is 12.

        title_fontsize : int, optional
            Font size of the subplot titles. Default is 12.

        gui_window : bool, optional
            If True (default), open a graphical user interface window for the plot.

        Returns
        -------
        Figure
            A Figure object containing plots of sediment inflow to the stream path.
        '''

        # check static type of input variable origin
        utility._validate_variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.sediment_inflow_to_stream
            ),
            vars_values=locals()
        )

        # check validity of figure file
        self._validate_figure_ext(
            figure_file=figure_file
        )

        # figure plot
        figure = matplotlib.pyplot.figure(
            figsize=(fig_width, fig_height)
        )
        subplot = figure.subplots(1, 2)

        # stream GeoDataFrame
        stream_gdf = geopandas.read_file(
            filename=stream_file
        )
        total_sediment = stream_gdf['cumsed_kg'].max()
        stream_gdf['sed_%'] = 100 * stream_gdf['sed_kg'] / total_sediment
        stream_gdf['cumsed_%'] = 100 * stream_gdf['cumsed_kg'] / total_sediment

        # plot sediment percentage
        sed_min = int(stream_gdf['sed_%'].min())
        sed_max = int(stream_gdf['sed_%'].max()) + 1
        stream_gdf.plot(
            column='sed_%',
            ax=subplot[0],
            cmap=sed_colormap,
            vmin=sed_min,
            vmax=sed_max,
            legend=True,
            legend_kwds={"shrink": 0.75},
            linewidth=stream_linewidth
        )
        subplot[0].set_title(
            label=sed_title,
            fontsize=title_fontsize
        )

        # plot cumulative sediment percentage
        cumsed_min = int(stream_gdf['cumsed_%'].min())
        stream_gdf.plot(
            column='cumsed_%',
            ax=subplot[1],
            cmap=cumsed_colormap,
            vmin=cumsed_min,
            legend=True,
            legend_kwds={"shrink": 0.75},
            linewidth=stream_linewidth
        )
        subplot[1].set_title(
            label=cumsed_title,
            fontsize=title_fontsize
        )

        # remove ticks and labels from both axes
        for i in [0, 1]:
            subplot[i].tick_params(
                axis='both',
                which='both',
                left=False,
                bottom=False,
                labelleft=False,
                labelbottom=False
            )

        # fix tick locations and labels in sediment inflow colorbar
        sed_cb = figure.get_axes()[2]
        sed_yticks = numpy.arange(0, sed_max + 0.01, sed_tickgap, dtype=type(sed_tickgap))
        sed_cb.set_yticks(
            ticks=sed_yticks
        )
        sed_cb.set_yticklabels(
            labels=[str(yt) for yt in sed_yticks],
            fontsize=tick_fontsize
        )

        # fix tick locations and labels in cumulative sediment inflow colorbar
        cumsed_cb = figure.get_axes()[3]
        cumsed_yticks = list(range(cumsed_min, 100 + 1, cumsed_tickgap))
        cumsed_cb.set_yticks(
            ticks=cumsed_yticks
        )
        cumsed_cb.set_yticklabels(
            labels=[str(yt) for yt in cumsed_yticks],
            fontsize=tick_fontsize
        )

        # saving figure
        figure.tight_layout()
        figure.savefig(
            fname=figure_file,
            bbox_inches='tight'
        )

        # figure display
        matplotlib.pyplot.show() if gui_window else None
        matplotlib.pyplot.close(figure)

        return figure

    def dam_location_in_stream(
        self,
        stream_file: str,
        dam_file: str,
        figure_file: str,
        fig_width: int | float = 6,
        fig_height: int | float = 6,
        fig_title: str = 'Dam locations with stream identifiers',
        stream_linewidth: int | float = 1,
        dam_marker: str = 'o',
        dam_markersize: int = 50,
        plot_damid: bool = True,
        damid_fontsize: int = 9,
        title_fontsize: int = 15,
        gui_window: bool = True
    ) -> matplotlib.figure.Figure:

        '''
        Generates a figure showing dam locations along the stream path, with an option to
        display the stream segment identifiers for each dam.

        Parameters
        ----------
        stream_file : str
            Path to the input stream vector file, created by one of:

            - :meth:`OptiDamTool.WatemSedem.dem_to_stream`
            - :meth:`OptiDamTool.Analysis.sediment_delivery_to_stream_geojson`

        dam_file : str
            Path to the input dam location vector file
            ``year_<start_year>_dam_location_point.geojson``, created by
            :meth:`OptiDamTool.Network.stodym_plus_with_drainage_scenarios`.

        figure_file : str
            Path to the output figure file.

        fig_width : float, optional
            Width of the figure in inches. Default is 6.

        fig_height : float, optional
            Height of the figure in inches. Default is 6.

        fig_title : str, optional
            Title of the figure. Default is 'Dam locations with identifiers'.

        stream_linewidth : float, optional
            Line width for plotting the stream. Default is 1.

        dam_marker : str, optional
            Marker style for dam points. Default is 'o'.

        dam_markersize : int, optional
            Marker size for dam points. Default is 50.

        plot_damid : bool, optional
            If True (default), plot stream segment identifiers for dams.

        damid_fontsize : int, optional
            Font size for stream segment identifier labels. Default is 9.

        title_fontsize : int, optional
            Font size of the figure title. Default is 15.

        gui_window : bool, optional
            If True (default), open a graphical user interface window for the plot.

        Returns
        -------
        Figure
            A Figure object containing the dam locations plotted on the stream path.
        '''

        # check static type of input variable origin
        utility._validate_variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.dam_location_in_stream
            ),
            vars_values=locals()
        )

        # check validity of figure file
        self._validate_figure_ext(
            figure_file=figure_file
        )

        # figure plot
        figure = matplotlib.pyplot.figure(
            figsize=(fig_width, fig_height)
        )
        subplot = figure.subplots(1, 1)

        # stream GeoDataFrame
        stream_gdf = geopandas.read_file(
            filename=stream_file
        )

        # dam GeoDataFrame
        dam_gdf = geopandas.read_file(
            filename=dam_file
        )

        # plot data
        stream_gdf.plot(
            ax=subplot,
            color='deepskyblue',
            linewidth=stream_linewidth,
            zorder=1
        )
        dam_gdf.plot(
            ax=subplot,
            color='orangered',
            marker=dam_marker,
            markersize=dam_markersize,
            zorder=2
        )

        # remove ticks and labels from both axes
        subplot.tick_params(
            axis='both',
            which='both',
            left=False,
            bottom=False,
            labelleft=False,
            labelbottom=False
        )

        # plot stream segment identifiers of dams
        if plot_damid:
            for dam_id, dam_coords in zip(dam_gdf['ws_id'], dam_gdf.geometry):
                # xc, yc = dam_coords.x, dam_coords.y
                subplot.text(
                    x=dam_coords.x,
                    y=dam_coords.y,
                    s=str(dam_id),
                    fontsize=damid_fontsize,
                    fontweight='bold',
                    ha='left',
                    va='center',
                    color='black',
                    zorder=3
                )

        # stream legend handle
        stream_legend = matplotlib.lines.Line2D(
            xdata=[0],
            ydata=[0],
            color='deepskyblue',
            linewidth=2,
            label='Stream'
        )

        # dam legend handle
        dam_legend = matplotlib.lines.Line2D(
            xdata=[0],
            ydata=[0],
            color='orangered',
            marker=dam_marker,
            markersize=10,
            linestyle='None',
            label='Dam'
        )

        # add custom legend
        subplot.legend(
            handles=[
                stream_legend,
                dam_legend
            ],
            loc='best'
        )

        # figure title
        figure.suptitle(
            fig_title,
            fontsize=title_fontsize
        )

        # saving figure
        figure.tight_layout()
        figure.savefig(
            fname=figure_file,
            bbox_inches='tight'
        )

        # figure display
        matplotlib.pyplot.show() if gui_window else None
        matplotlib.pyplot.close(figure)

        return figure

    def system_statistics(
        self,
        json_file: str,
        figure_file: str,
        fig_width: int | float = 10,
        fig_height: int | float = 5,
        fig_title: str = 'Dam system statistics',
        plot_storage: bool = True,
        plot_trap: bool = True,
        plot_release: bool = True,
        plot_drainage: bool = True,
        system_linewidth: int | float = 3,
        xtick_gap: int = 10,
        ytop_offset: int | float = 0,
        ybottom_offset: int | float = 0,
        legend_loc: str = 'best',
        legend_fontsize: int = 12,
        tick_fontsize: int = 12,
        axis_fontsize: int = 15,
        title_fontsize: int = 15,
        gui_window: bool = True
    ) -> matplotlib.figure.Figure:

        '''
        Generates a figure summarizing dam system statistics with annual percent changes for key metrics:

        - **Total remaining storage** across all dams, relative to the initial total storage
          at the start of each simulation year.
        - **Total sediment trapped** by all dams, relative to the total sediment input across
          all stream segments during the simulation year.
        - **Sediment released** by terminal dams and by drainage areas not covered by the dam system,
          relative to the total sediment input across all stream segments during the simulation year.
        - **Total controlled drainage area** across all dams, relative to the total stream drainage area
          at the start of each simulation year.

        Parameters
        ----------
        json_file : str
            Path to the input ``system_statistics.json`` file, created by one of the methods:

            - :meth:`OptiDamTool.Network.stodym_plus`
            - :meth:`OptiDamTool.Network.stodym_plus_with_drainage_scenarios`

        figure_file : str
            Path to the output figure file.

        fig_width : float, optional
            Width of the figure in inches. Default is 10.

        fig_height : float, optional
            Height of the figure in inches. Default is 5.

        fig_title : str, optional
            Title of the figure. Default is 'Dam system statistics'.

        plot_storage : bool, optional
            If True (default), include the annual percent change in total remaining storage across all dams.

        plot_trap : bool, optional
            If True (default), include the annual percent change in total sediment trapped by all dams.

        plot_release : bool, optional
            If True (default), include the annual percent change in sediment released by terminal dams and
            by drainage areas not covered by the dam system.

        plot_drainage : bool, optional
            If True (default), include the annual percent change in total controlled drainage area across all dams.

        system_linewidth : float, optional
            Line width for plotting the system statistics. Default is 3.

        xtick_gap : int, optional
            Gap between two x-axis ticks. Default is 10.

        ytop_offset : float, optional
            Positive offset to increase the upper y-axis limit above 100, improving visibility
            when plot values are close to 100. Default is 0.

        ybottom_offset : float, optional
            Negative offset to decrease the lower y-axis limit below 0, improving visibility
            when plot values are close to 0. Default is 0.

        legend_loc : str, optional
            Location of the legend in the figure. Default is 'best'.

        legend_fontsize : int, optional
            Font size of the legend. Default is 12.

        tick_fontsize : int, optional
            Font size of the tick labels on both axes. Default is 12.

        axis_fontsize : int, optional
            Font size of the axis labels. Default is 15.

        title_fontsize : int, optional
            Font size of the figure title. Default is 15.

        gui_window : bool, optional
            If True (default), open a graphical user interface window of the plot.

        Returns
        -------
        Figure
            A Figure object containing the dam system statistics plots.

            .. note::

                Users can choose to plot all four metrics or only a subset of them by setting the
                corresponding boolean parameters to ``False``.
        '''

        # check static type of input variable origin
        utility._validate_variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.system_statistics
            ),
            vars_values=locals()
        )

        # check validity of figure file
        self._validate_figure_ext(
            figure_file=figure_file
        )

        # figure plot
        figure = matplotlib.pyplot.figure(
            figsize=(fig_width, fig_height)
        )
        subplot = figure.subplots(1, 1)

        # Check that at least one plot option is enabled
        check_plot = [plot_storage, plot_trap, plot_release, plot_drainage]
        if check_plot == [False] * len(check_plot):
            raise ValueError('At least one plot type must be set to True')

        # system statistics DataFrame
        df = pandas.read_json(
            path_or_buf=json_file,
            orient='records'
        )

        # plot remaining storage percentage
        if plot_storage:
            subplot.plot(
                df['start_year'], df['storage_%'],
                linestyle='-',
                linewidth=system_linewidth,
                color='cyan',
                label='Remaining storage'
            )

        # plot trapped sediment percentage
        if plot_trap:
            subplot.plot(
                df['start_year'], df['sedtrap_%'],
                linestyle='-',
                linewidth=system_linewidth,
                color='forestgreen',
                label='Sediment trapped'
            )

        # plot released sediment percentage
        if plot_release:
            subplot.plot(
                df['start_year'], df['sedrelease_%'],
                linestyle='-',
                linewidth=system_linewidth,
                color='red',
                label='Sediment released'
            )

        # plot controlled drainage area percentage
        if plot_drainage:
            subplot.plot(
                df['start_year'], df['drainage_%'],
                linestyle='-',
                linewidth=system_linewidth,
                color='goldenrod',
                label='Controlled drainage'
            )

        # legend
        subplot.legend(
            loc=legend_loc,
            fontsize=legend_fontsize
        )

        # x-axis customization
        year_max = df['start_year'].max()
        xaxis_max = (int(year_max / xtick_gap) + 1) * xtick_gap
        subplot.set_xlim(
            left=0,
            right=xaxis_max
        )
        xticks = range(0, xaxis_max + 1, xtick_gap)
        subplot.set_xticks(
            ticks=xticks
        )
        subplot.set_xticklabels(
            labels=[str(xt) for xt in xticks],
            fontsize=12
        )
        subplot.tick_params(
            axis='x',
            which='both',
            direction='in',
            length=6,
            width=1,
            top=True,
            bottom=True,
            labeltop=False,
            labelbottom=True
        )
        subplot.grid(
            visible=True,
            which='major',
            axis='x',
            color='gray',
            linestyle='--',
            linewidth=0.3
        )
        subplot.set_xlabel(
            xlabel='Year',
            fontsize=axis_fontsize
        )

        # y-axis customization
        subplot.set_ylim(
            bottom=0 + ybottom_offset,
            top=100 + ytop_offset
        )
        yticks = range(0, 100 + 1, 10)
        subplot.set_yticks(
            ticks=yticks
        )
        subplot.set_yticklabels(
            labels=[str(yt) for yt in yticks],
            fontsize=tick_fontsize
        )
        subplot.tick_params(
            axis='y',
            which='both',
            direction='in',
            length=6,
            width=1,
            left=True,
            right=True,
            labelleft=True,
            labelright=False
        )
        subplot.grid(
            visible=True,
            which='major', axis='y',
            color='gray',
            linestyle='--', linewidth=0.3
        )
        subplot.set_ylabel(
            ylabel='Percentage (%)',
            fontsize=axis_fontsize
        )

        # figure title
        figure.suptitle(
            fig_title,
            fontsize=title_fontsize
        )

        # saving figure
        figure.tight_layout()
        figure.savefig(
            fname=figure_file,
            bbox_inches='tight'
        )

        # figure display
        matplotlib.pyplot.show() if gui_window else None
        matplotlib.pyplot.close(figure)

        return figure

    def dam_individual_features(
        self,
        json_file: str,
        figure_file: str,
        fig_width: int | float = 10,
        fig_height: int | float = 5,
        fig_title: str = '',
        colormap_name: str = 'coolwarm',
        dam_linewidth: int | float = 2,
        xtick_gap: int = 10,
        ytick_gap: int | float = 10,
        ytop_offset: int | float = 0,
        ybottom_offset: int | float = 0,
        legend_cols: int = 1,
        legend_fontsize: int = 12,
        tick_fontsize: int = 12,
        axis_fontsize: int = 15,
        title_fontsize: int = 15,
        gui_window: bool = True
    ) -> matplotlib.figure.Figure:

        '''
        Generate a figure illustrating the annual variability of key features for each dam in the system.
        The input data are produced by the methods :meth:`OptiDamTool.Network.stodym_plus` and
        :meth:`OptiDamTool.Network.stodym_plus_with_drainage_scenarios`.

        - ``dam_drainage_area.json``
            Percentage of the controlled drainage area for each dam, relative to the total stream drainage area,
            evaluated at the start of the simulation year.

        - ``dam_remaining_storage.json``
            Remaining storage capacity as a percentage of the dam’s initial storage, evaluated at the start of the simulation year.

        - ``dam_trap_efficiency.json``
            Trap efficiency expressed as a percentage, evaluated at the start of the simulation year.

        - ``dam_trapped_sediment.json``
            Percentage of sediment trapped by the dam, relative to the total sediment input across all stream segments,
            evaluated at the end of the simulation year.

        Parameters
        ----------
        json_file : str
            Path to the JSON file containing the dam feature data.

        figure_file : str
            Path to the output figure file.

        fig_width : float, optional
            Width of the figure in inches. Default is 10.

        fig_height : float, optional
            Height of the figure in inches. Default is 5.

        fig_title : str, optional
            Title of the figure. Default is 'Dam annual sediment trapping'.

        colormap_name : str, optional
            Name of the `colormap <https://matplotlib.org/stable/users/explain/colors/colormaps.html>`_
            used to generate colors for individual dams. Default is 'coolwarm'.

        dam_linewidth : float, optional
            Line width for plotting the storage variation of individual dams. Default is 2.

        xtick_gap : int, optional
            Gap between two x-axis ticks. Default is 10.

        ytick_gap : float, optional
            Gap between two y-axis ticks. Default is 10.

        ytop_offset : float, optional
            Positive offset to increase the upper y-axis limit above 100, improving visibility
            when plot values are close to 100. Default is 0.

        ybottom_offset : float, optional
            Negative offset to decrease the lower y-axis limit below 0, improving visibility
            when plot values are close to 0. Default is 0.

        legend_cols : int, optional
            Number of columns to arrange legend items. Default is 1.

        legend_fontsize : int, optional
            Font size of the legend. Default is 12.

        tick_fontsize : int, optional
            Font size of the tick labels on both axes. Default is 12.

        axis_fontsize : int, optional
            Font size of the axis labels. Default is 15.

        title_fontsize : int, optional
            Font size of the figure title. Default is 15.

        gui_window : bool, optional
            If True (default), open a graphical user interface window of the plot.

        Returns
        -------
        Figure
            A Figure object containing the annual sediment trapping percentage by each dam in the system.
        '''

        # check static type of input variable origin
        utility._validate_variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.dam_individual_features
            ),
            vars_values=locals()
        )

        # check validity of figure file
        self._validate_figure_ext(
            figure_file=figure_file
        )

        # setting figure
        figure = matplotlib.pyplot.figure(
            figsize=(fig_width, fig_height)
        )
        figure_grid = figure.add_gridspec(
            nrows=1,
            ncols=5
        )

        # setting subplot
        plot_data = figure.add_subplot(figure_grid[0, :4])

        # setting subplot for legend
        plot_legend = figure.add_subplot(figure_grid[0, 4])

        # DataFrame
        df = pandas.read_json(
            path_or_buf=json_file,
            orient='records'
        )

        # remove values that are not required
        df = df.where(
            cond=(df >= 0) & (df <= 100)
        )

        # sort dam columns
        dam_cols = sorted(
            [col for col in df.columns if col != 'start_year'],
            key=int
        )

        # set colors
        colormap = matplotlib.colormaps.get_cmap(
            cmap=colormap_name
        )
        color_dict = {
            dam_cols[i]: colormap(i / len(dam_cols)) for i in range(len(dam_cols))
        }

        # plot dam features
        legend_handles = []
        for dam in dam_cols:
            dam_line2d = plot_data.plot(
                df['start_year'], df[dam],
                linestyle='-',
                linewidth=dam_linewidth,
                color=color_dict[dam]
            )
            legend_handles.append(dam_line2d[0])

        # plot legend
        plot_legend.legend(
            handles=legend_handles,
            labels=dam_cols,
            loc='center',
            fontsize=legend_fontsize,
            ncols=legend_cols,
            frameon=False
        )
        plot_legend.axis('off')

        # x-axis customization
        year_max = df['start_year'].max()
        xaxis_max = (int(year_max / xtick_gap) + 1) * xtick_gap
        plot_data.set_xlim(
            left=0,
            right=xaxis_max
        )
        xticks = range(0, xaxis_max + 1, xtick_gap)
        plot_data.set_xticks(
            ticks=xticks
        )
        plot_data.set_xticklabels(
            labels=[str(xt) for xt in xticks],
            fontsize=12
        )
        plot_data.tick_params(
            axis='x',
            which='both',
            direction='in',
            length=6,
            width=1,
            top=True,
            bottom=True,
            labeltop=False,
            labelbottom=True
        )
        plot_data.grid(
            visible=True,
            which='major',
            axis='x',
            color='gray',
            linestyle='--',
            linewidth=0.3
        )
        plot_data.set_xlabel(
            xlabel='Year',
            fontsize=axis_fontsize
        )

        # y-axis customization
        df_max = df[dam_cols].max().max()
        yaxis_ub = (int(df_max / ytick_gap) + 1) * ytick_gap
        yaxis_max = yaxis_ub if yaxis_ub < 100 else 100
        plot_data.set_ylim(
            bottom=0 + ybottom_offset,
            top=yaxis_max + ytop_offset
        )
        yticks = numpy.arange(0, yaxis_max + 0.01, ytick_gap, dtype=type(ytick_gap))
        plot_data.set_yticks(
            ticks=yticks
        )
        plot_data.set_yticklabels(
            labels=[str(yt) for yt in yticks],
            fontsize=tick_fontsize
        )
        plot_data.tick_params(
            axis='y',
            which='both',
            direction='in',
            length=6,
            width=1,
            left=True,
            right=True,
            labelleft=True,
            labelright=False
        )
        plot_data.grid(
            visible=True,
            which='major',
            axis='y',
            color='gray',
            linestyle='--',
            linewidth=0.3
        )
        plot_data.set_ylabel(
            ylabel='Percentage (%)',
            fontsize=axis_fontsize
        )

        # figure title
        figure.suptitle(
            fig_title,
            fontsize=title_fontsize
        )

        # saving figure
        figure.tight_layout()
        figure.savefig(
            fname=figure_file,
            bbox_inches='tight'
        )

        # figure display
        matplotlib.pyplot.show() if gui_window else None
        matplotlib.pyplot.close(figure)

        return figure
