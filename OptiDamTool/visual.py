import matplotlib
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
        fig_title: str = 'Dam locations with stream indentifiers',
        line_width: float = 1,
        dam_marker: str = 'o',
        dam_markersize: float = 50,
        dam_fontsize: int = 9,
        title_fontsize: int = 15,
        gui_window: bool = True
    ) -> matplotlib.figure.Figure:

        '''
        .. warning::

            This function is under development and should not be used.
        '''

        # stream GeoDataFrame
        stream_gdf = geopandas.read_file(
            filename=stream_file
        )

        # dam GeoDataFrame
        dam_gdf = geopandas.read_file(
            filename=dam_file
        )

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

        # plot data
        stream_gdf.plot(
            ax=subplot,
            color='deepskyblue',
            linewidth=line_width,
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

        # label each dam with its stream identifiers
        for dam_id, dam_coords in zip(dam_gdf['ws_id'], dam_gdf.geometry):
            xc, yc = dam_coords.x, dam_coords.y
            subplot.text(
                xc, yc,
                str(dam_id),
                fontsize=dam_fontsize,
                fontweight='bold',
                ha='left',
                va='center',
                color='black',
                zorder=3
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
        fig_width: float = 12,
        fig_height: float = 6,
        fig_title: str = 'Dam system statistics',
        xtick_gap: int = 10,
        legend_loc: str = 'best',
        legend_fontsize: int = 12,
        tick_fontsize: int = 12,
        axis_fontsize: int = 15,
        title_fontsize: int = 15,
        gui_window: bool = True
    ) -> matplotlib.figure.Figure:

        '''
        Generates a figure of dam system statistics, including plots of:

        - Yearly percentage of total remaining storage across all dams relative
          to the initial total storage, at the beginning of the simulation year.
        - Yearly percentage of total sediment trapped by all dams relative
          to the total sediment input across all stream segments during the simulation year.
        - Yearly percentage of sediment released by terminal dams and drainage areas
          not covered by the dam system, relative to the total sediment input across
          all stream segments during the simulation year.

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
            Width of the figure in inches. Default is 12.

        fig_height : float, optional
            Height of the figure in inches. Default is 6.

        fig_title : str, optional
            Title of the figure. Default is 'Dam system statistics'.

        xtick_gap : int, optional
            Gap between two x-axis ticks. Default is 10.

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
            If True, open a graphical user interface window of the plot. Default is True.

        Returns
        -------
        Figure
            A Figure object containing the dam system statistics plots.
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

        # system statistics DataFrame
        df = pandas.read_json(
            path_or_buf=json_file,
            orient='records',
            lines=True
        )

        # plot data
        subplot.plot(
            df['start_year'], df['storage_%'],
            linestyle='-',
            linewidth=3,
            color='cyan',
            label='Remaining storage'
        )
        subplot.plot(
            df['start_year'], df['sedtrap_%'],
            linestyle='-',
            linewidth=3,
            color='forestgreen',
            label='Sediment trapped'
        )
        subplot.plot(
            df['start_year'], df['sedrelease_%'],
            linestyle='-',
            linewidth=3,
            color='red',
            label='Sediment released'
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
