from Scrape_pokemon_functions import filter_top_finishes
import shinyswatch

from pathlib import Path

from shared import ex_list, dropdown_df, image_dict, expansions, ex_list2

from Scrape_pokemon_functions import create_finishes_df, power_ranking_table, filter_nonex_frame, get_partners

from shiny import App, render, ui

import re

#import matplotlib.pyplot as plt
import plotly.express as px
from shinywidgets import output_widget, render_widget
here = Path(__file__).parent

app_ui = ui.page_navbar(

    ui.nav_panel("Competitive History",

ui.page_fluid(

        ui.div({"style": """
                    display: flex;
                    align-items: center;
                    gap: 10px;
                """},
            ui.panel_title(ui.output_image("ptcgp",inline=True)),
            ui.h3("Pokémon TCGP A-Series Competitive Dashboard")
        ),
    ui.layout_sidebar(
        
        ui.sidebar(

        ui.input_selectize(  
        "select", 
        "Select ex card:", 
        choices=ex_list),
        ui.output_image("pics"),width=285),

        ui.card(
            
            output_widget("plot")),
        ),
        ui.navset_card_tab(

            ui.nav_panel("Best Performance",
            ui.layout_columns(
                ui.card(
                    ui.card_header("Best Tournament Placement"),
                    ui.value_box(
                        ui.output_text("player_best"),
                        ui.output_text("deck_best"),
                        ui.output_text("record_best"),
                        ui.output_text("placement_best"),
                        ui.output_text("date_best"),
                        ui.output_text("tournament_best"))),
            ui.card(
                ui.card_header("Total Placements"),

            ui.output_data_frame("finishes")),
            
            ui.card(
                ui.card_header("Best Partners",),
                output_widget("partners"),
            ))),

            ui.nav_panel("By Expansion",

                ui.input_selectize(
                    "select2",
                    "Select expansion",
                    choices = expansions),

                ui.layout_columns(

                    ui.card(
                        ui.card_header('Best Performance'),
                        ui.value_box(
                        ui.output_text("player"),
                        ui.output_text("deck"),
                        ui.output_text("record"),
                        ui.output_text("placement"),
                        ui.output_text("date"),
                        ui.output_text("tournament"))
                    ),
                    ui.card(
                        ui.card_header('Total Placements'),
                        ui.output_data_frame("finishes2")
                    ),
                    ui.card(
                        ui.card_header('Best Partners'),
                        output_widget("partners2")
                    ),
                col_widths=(4,4,4))
        )
        )
        )
    ),
    ui.nav_panel("Most Dominant",
        ui.div({"style": """
                    display: flex;
                    align-items: center;
                    gap: 15px;
                """},
            ui.h3("Exploration of Most Dominant Pokémon"),
            ui.panel_title(ui.output_image('exlogo',inline=True)),
        ),
        ui.layout_columns(
        ui.card(),
        ui.card(
            ui.card_header("Weighted Score"),
            ui.output_data_frame("dominant"),
            ui.card_footer("Weighted Score is based off of all top finishes weighted to account for increasing power level and decreasing player counts in the metagame.")
        ),
    col_widths=(8,4))),
    
    ui.nav_panel("Other cards",
    ui.layout_columns(
        ui.card(
            ui.card_header("Search any other card to see its tournament success, like a non-ex Pokémon, or a supporter"),
            ui.card_header('Tip: Since some cards have similar or identical names, use the card id (i.e. "A2b-3") for more exact results if necessary'),
            ui.input_text("text", "Pokémon name", "Greninja"),
            ui.output_data_frame("nonex")),
        ui.card(
            ui.output_data_frame("nonexfinishes")
        ), col_widths=(10,2))
    ),
    theme=shinyswatch.theme.zephyr)


def server(input, output, session):
    def make_row():
        if input.select() == 'Charizard ex: A1':
            selected = 'A1-36'
        elif input.select() == 'Charizard ex: A2b':
            selected = 'A2b-10'
        elif input.select() == 'Pikachu ex: A1':
            selected = 'A1-96'
        elif input.select() == 'Pikachu ex: A2b':
            selected = 'A2b-22'
        else:
            selected = input.select()
        selected2=input.select2()
        df = dropdown_df[dropdown_df['Decklists'].str.contains(selected)]
        try:
            row1 = df[(df['Expansion'] == selected2) & (df['Player_Total'] > 300)].sort_values(['Placement','Player_Total'], ascending=[True, False]).iloc[0]
        except IndexError:
            row1 = None
        row2 = df[df['Player_Total'] > 300].sort_values(['Placement','Player_Total'], ascending=[True, False]).iloc[0]
        return row1, row2
    @render.text
    def deck():
        a,b = make_row()
        if a is None:
            return "No placements or not yet released"
        else:
            return a['Deck']
    @render.text
    def player():
        a,b = make_row()
        if a is None:
            return None
        else:
            return a['Player']
    @render.text
    def record():
        a,b = make_row()
        if a is None:
            return None
        else:
            return a['Score']
    @render.text
    def tournament():
        a,b = make_row()
        if a is None:
            return None
        else:
            return a['Tournament']
    @render.text
    def date():
        a,b = make_row()
        if a is None:
            return None
        else:
            return a['Date']
    @render.text
    def placement():
        a,b = make_row()
        if a is None:
            return None
        else:
            line = f'{int(a['Placement'])} out of {int(a['Player_Total'])}'
            return line
    @render.text
    def deck_best():
        a,b = make_row()
        return b['Deck']
    @render.text
    def player_best():
        a,b = make_row()
        return b['Player']
    @render.text
    def record_best():
        a,b = make_row()
        return b['Score']
    @render.text
    def tournament_best():
        a,b = make_row()
        return b['Tournament']
    @render.text
    def date_best():
        a,b = make_row()
        return b['Date']
    @render.text
    def placement_best():
        a,b = make_row()
        line = f'{int(b['Placement'])} out of {int(b['Player_Total'])}'
        return line
    @render.text
    def expansion_best():
        a,b = make_row()
        return b['Expansion']
    @render.image
    def pics():
        selected=input.select()
        images = image_dict
        image = images.get(selected).copy()
        image['src'] = here / image['src']
        return image
    @render.image
    def ptcgp():
        img = {"src": here / 'www/ptcgp_icon.png', "height": "80px","style":"padding-bottom:20px"}
        return img
    @render.image
    def exlogo():
        img = {"src": here / 'www/exlogo.png', "height": "45px","style":"padding-bottom:15px"}
        return img
    # @render_widget
    # def plot():
    #     if input.select() == 'Charizard ex: A1':
    #         selected = 'A1-36'
    #     elif input.select() == 'Charizard ex: A2b':
    #         selected = 'A2b-10'
    #     elif input.select() == 'Pikachu ex: A1':
    #         selected = 'A1-96'
    #     elif input.select() == 'Pikachu ex: A2b':
    #         selected = 'A2b-22'
    #     else:
    #         selected = input.select()
    #     df = dropdown_df[dropdown_df['Decklists'].str.contains(selected)]
    #     Expansion = df['Expansion'].unique()
    #     Placement = [df[(df['Expansion'] == expansion) & (df['Player_Total'] > 300)]['Placement'].sort_values()[:10].mean() for expansion in df['Expansion'].unique()]
    #     fig = px.line(x=Expansion,y=Placement,markers=True)
    #     return fig
    @render.data_frame
    def finishes():
        if input.select() == 'Charizard ex: A1':
            selected = 'A1-36'
        elif input.select() == 'Charizard ex: A2b':
            selected = 'A2b-10'
        elif input.select() == 'Pikachu ex: A1':
            selected = 'A1-96'
        elif input.select() == 'Pikachu ex: A2b':
            selected = 'A2b-22'
        else:
            selected = input.select()
        df = dropdown_df[dropdown_df['Decklists'].str.contains(selected)]
        df_to_use = df[(df['Player_Total'] > 200) & (df['Placement'] <= 64)]
        final_df = create_finishes_df(df_to_use)
        return render.DataTable(final_df,width="500px",
        styles=[
                {
                    "style": {"font-size": "15px"}
                }
        ])
    @render.data_frame
    def finishes2():
        if input.select() == 'Charizard ex: A1':
            selected = 'A1-36'
        elif input.select() == 'Charizard ex: A2b':
            selected = 'A2b-10'
        elif input.select() == 'Pikachu ex: A1':
            selected = 'A1-96'
        elif input.select() == 'Pikachu ex: A2b':
            selected = 'A2b-22'
        else:
            selected = input.select()
        selected2 = input.select2()
        df = dropdown_df[dropdown_df['Expansion'] == selected2]
        df_to_use = filter_top_finishes(df, selected)
        final_df = create_finishes_df(df_to_use)
        return render.DataTable(final_df,width="500px",
        styles=[
                {
                    "style": {"font-size": "15px"}
                }
        ])
    @render_widget
    def partners():
        selected = input.select()
        data = get_partners(dropdown_df, selected)
        fig = px.bar(data, x='Partner', y='Count',height=300)
        fig['layout']['yaxis']['autorange'] = "reversed"
        fig.update_xaxes(title=None)
        fig.update_yaxes(title=None)
        fig.update_traces(hovertemplate='Count: %{y}')
        return fig
    @render_widget
    def partners2():
        selected = input.select()
        selected2 = input.select2()
        df = dropdown_df[dropdown_df['Expansion'] == selected2]
        data = get_partners(df, selected)
        fig = px.bar(data, x='Partner', y='Count',height=300)
        fig['layout']['yaxis']['autorange'] = "reversed"
        fig.update_xaxes(title=None)
        fig.update_yaxes(title=None)
        fig.update_traces(hovertemplate='Count: %{y}')
        return fig
    @render.data_frame
    def dominant():
        power_rankings = power_ranking_table(dropdown_df, ex_list2)
        return render.DataGrid(power_rankings[['Pokémon','Score']],summary=False,width="800px",
        styles=[
                {
                    "style": {"font-size": "20px"}
                }
        ])
    @render.data_frame
    def nonex():
        regex = re.compile(r'A[1234][ab]?-\d{1,3}')
        cardid = input.text()
        if re.match(regex, cardid):
            df = filter_nonex_frame(dropdown_df, cardid)
        else:
            df = dropdown_df[dropdown_df['Decklists'].str.contains(cardid)]
        return render.DataTable(df[['Deck','Placement','Player_Total','Score','Player','Date','Tournament']],filters=True)
    @render.data_frame
    def nonexfinishes():
        pokemon = input.text()
        df = dropdown_df[dropdown_df['Decklists'].str.contains(pokemon)]
        df_to_use = df[(df['Player_Total'] > 200) & (df['Placement'] <= 64)]
        final_df = create_finishes_df(df_to_use)
        return render.DataTable(final_df)

app = App(app_ui, server)