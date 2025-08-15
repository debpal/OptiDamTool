import matplotlib
import matplotlib.lines
import matplotlib.pyplot
import pandas
import geopandas
import os


class Visual:

    '''
    Provides utilities for visualizing data.
    '''

    def dam_location_in_stream(
        self,
        stream_file: str,
        dam_file: str,
        figure_file: str,
        fig_width: float = 6,
        fig_height: float = 6,
        fig_title: str = 'Dam locations with identifiers',
        stream_linewidth: float = 1,
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
            :meth:`OptiDamTool.Network.storage_dynamics_and_drainage_scenarios`.

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

        # figure plot
        figure = matplotlib.pyplot.figure(
            figsize=(fig_width, fig_height)
        )
        subplot = figure.subplots(1, 1)

        # check figure file extension
        fig_ext = os.path.splitext(figure_file)[-1][1:]
        if fig_ext not in list(figure.canvas.get_supported_filetypes().keys()):
            raise ValueError(
                f'Input figure_file extension ".{fig_ext}" is not supported for saving the figure.'
            )

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
        fig_width: float = 10,
        fig_height: float = 5,
        fig_title: str = 'Dam system statistics',
        plot_storage: bool = True,
        plot_trap: bool = True,
        plot_release: bool = True,
        plot_drainage: bool = True,
        system_linewidth: float = 3,
        xtick_gap: int = 10,
        ytop_offset: int = 0,
        ybottom_offset: int = 0,
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

            - :meth:`OptiDamTool.Network.storage_dynamics_detailed`
            - :meth:`OptiDamTool.Network.storage_dynamics_lite`
            - :meth:`OptiDamTool.Network.storage_dynamics_and_drainage_scenarios`

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

        ytop_offset : int, optional
            Positive offset to increase the upper y-axis limit above 100, improving visibility
            when plot values are close to 100. Default is 0.

        ybottom_offset : int, optional
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

        # figure plot
        figure = matplotlib.pyplot.figure(
            figsize=(fig_width, fig_height)
        )
        subplot = figure.subplots(1, 1)

        # check figure file extension
        fig_ext = os.path.splitext(figure_file)[-1][1:]
        if fig_ext not in list(figure.canvas.get_supported_filetypes().keys()):
            raise ValueError(
                f'Input figure_file extension ".{fig_ext}" is not supported for saving the figure.'
            )

        # Check that at least one plot option is enabled
        check_plot = [plot_storage, plot_trap, plot_release, plot_drainage]
        if check_plot == [False] * len(check_plot):
            raise ValueError('At least one plot type must be set to True.')

        # system statistics DataFrame
        df = pandas.read_json(
            path_or_buf=json_file,
            orient='records',
            lines=True
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
        subplot.set_xlim(0, xaxis_max)
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
        subplot.set_ylim(0 + ybottom_offset, 100 + ytop_offset)
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

    def dam_remaining_storage(
        self,
        json_file: str,
        figure_file: str,
        fig_width: float = 10,
        fig_height: float = 5,
        fig_title: str = 'Dam annual storage variations',
        colormap_name: str = 'coolwarm',
        dam_linewidth: float = 2,
        xtick_gap: int = 10,
        legend_loc: str = 'upper right',
        legend_rows: int = 2,
        legend_fontsize: int = 12,
        tick_fontsize: int = 12,
        axis_fontsize: int = 15,
        title_fontsize: int = 15,
        gui_window: bool = True
    ) -> matplotlib.figure.Figure:

        '''
        Generates a figure showing the annual remaining storage of each dam in the system at the beginning of the year.

        Parameters
        ----------
        json_file : str
            Path to the input ``dam_remaining_storage.json`` file, created by one of the methods:

            - :meth:`OptiDamTool.Network.storage_dynamics_detailed`
            - :meth:`OptiDamTool.Network.storage_dynamics_lite`
            - :meth:`OptiDamTool.Network.storage_dynamics_and_drainage_scenarios`

        figure_file : str
            Path to the output figure file.

        fig_width : float, optional
            Width of the figure in inches. Default is 10.

        fig_height : float, optional
            Height of the figure in inches. Default is 5.

        fig_title : str, optional
            Title of the figure. Default is 'Dam annual storage variations'.

        colormap_name : str, optional
            Name of the `colormap <https://matplotlib.org/stable/users/explain/colors/colormaps.html>`_
            used to generate colors for individual dams. Default is 'coolwarm'.

        dam_linewidth : float, optional
            Line width for plotting the storage variation of individual dams. Default is 2.

        xtick_gap : int, optional
            Gap between two x-axis ticks. Default is 10.

        legend_loc : str, optional
            Location of the legend in the figure. Default is 'upper right'.

        legend_rows : int, optional
            Number of horizontal rows to arrange legend items. Default is 2.

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
            A Figure object containing the annual storage variation of each individual dam in the system.
        '''

        # figure plot
        figure = matplotlib.pyplot.figure(
            figsize=(fig_width, fig_height)
        )
        subplot = figure.subplots(1, 1)

        # check figure file extension
        fig_ext = os.path.splitext(figure_file)[-1][1:]
        if fig_ext not in list(figure.canvas.get_supported_filetypes().keys()):
            raise ValueError(
                f'Input figure_file extension ".{fig_ext}" is not supported for saving the figure.'
            )

        # dam remaining storage DataFrame
        df = pandas.read_json(
            path_or_buf=json_file,
            orient='records',
            lines=True
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

        # plot remaining storage percentage
        for dam in dam_cols:
            subplot.plot(
                df['start_year'], df[dam],
                linestyle='-',
                linewidth=dam_linewidth,
                color=color_dict[dam],
                label=dam
            )

        # legend
        subplot.legend(
            loc=legend_loc,
            fontsize=legend_fontsize,
            ncol=int(len(dam_cols) / legend_rows) + 1
        )

        # x-axis customization
        year_max = df['start_year'].max()
        xaxis_max = (int(year_max / xtick_gap) + 1) * xtick_gap
        subplot.set_xlim(0, xaxis_max)
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
        subplot.set_ylim(0, 100)
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

    def dam_trapped_sediment(
        self,
        json_file: str,
        figure_file: str,
        fig_width: float = 10,
        fig_height: float = 5,
        fig_title: str = 'Dam annual sediment trapping',
        colormap_name: str = 'coolwarm',
        dam_linewidth: float = 2,
        xtick_gap: int = 10,
        ytick_gap: int = 10,
        ybottom_offset: float = 0,
        legend_loc: str = 'upper right',
        legend_rows: int = 2,
        legend_fontsize: int = 12,
        tick_fontsize: int = 12,
        axis_fontsize: int = 15,
        title_fontsize: int = 15,
        gui_window: bool = True
    ) -> matplotlib.figure.Figure:

        '''
        Generates a figure showing the annual sediment trapping percentage by each dam in the system,
        relative to the total sediment input across all stream segments during the year.

        Parameters
        ----------
        json_file : str
            Path to the input ``dam_trapped_sediment.json`` file, created by one of the methods:

            - :meth:`OptiDamTool.Network.storage_dynamics_detailed`
            - :meth:`OptiDamTool.Network.storage_dynamics_lite`
            - :meth:`OptiDamTool.Network.storage_dynamics_and_drainage_scenarios`

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

        ytick_gap : int, optional
            Gap between two y-axis ticks. Default is 10.

        ybottom_offset : float, optional
            Negative offset to decrease the lower y-axis limit below 0, improving visibility
            when plot values are close to 0. Default is 0.

        legend_loc : str, optional
            Location of the legend in the figure. Default is 'upper right'.

        legend_rows : int, optional
            Number of horizontal rows to arrange legend items. Default is 2.

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

        # figure plot
        figure = matplotlib.pyplot.figure(
            figsize=(fig_width, fig_height)
        )
        subplot = figure.subplots(1, 1)

        # check figure file extension
        fig_ext = os.path.splitext(figure_file)[-1][1:]
        if fig_ext not in list(figure.canvas.get_supported_filetypes().keys()):
            raise ValueError(
                f'Input figure_file extension ".{fig_ext}" is not supported for saving the figure.'
            )

        # dam remaining storage DataFrame
        df = pandas.read_json(
            path_or_buf=json_file,
            orient='records',
            lines=True
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

        # plot remaining storage percentage
        for dam in dam_cols:
            subplot.plot(
                df['start_year'], df[dam],
                linestyle='-',
                linewidth=dam_linewidth,
                color=color_dict[dam],
                label=dam
            )

        # legend
        subplot.legend(
            loc=legend_loc,
            fontsize=legend_fontsize,
            ncol=int(len(dam_cols) / legend_rows) + 1
        )

        # x-axis customization
        year_max = df['start_year'].max()
        xaxis_max = (int(year_max / xtick_gap) + 1) * xtick_gap
        subplot.set_xlim(0, xaxis_max)
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
        trap_max = df[dam_cols].max().max()
        yaxis_max = (int(trap_max / ytick_gap) + 2) * ytick_gap
        subplot.set_ylim(0 + ybottom_offset, yaxis_max)
        yticks = range(0, yaxis_max + 1, ytick_gap)
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
