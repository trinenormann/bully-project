# My first Streamlit-app - comparing the amount of bullying in Norwegian high schools

import streamlit as st
import pandas as pd
import requests


def main():
    st.title("Bullying in Norwegian high schools")
    st.write("This table displays the amount of bullying in high schools in your chosen county.")
    st.write("Please note: The numbers for some schools are shielded (*) to protect the privacy of the students.")

    # Get latitude and longitude of school based on organization number
    def get_coordinates(orgnr):
        base_url = "https://data-nsr.udir.no/v3/enhet/"
        url = base_url + orgnr
        response = requests.get(url)
        return response.json()['Koordinat']['Breddegrad'], response.json()['Koordinat']['Lengdegrad']

    # Get data on bullying for all schools in a county
    @st.cache_data
    def get_bullydata(fylkenr):
        base_url = "https://api.statistikkbanken.udir.no/api/rest/v2/Eksport/154/data?filter="
        filters = f"EierformID(-10)_EnhetNivaa(3)_Fylkekode({fylkenr})_GruppeNivaa(0)_KjoennID(-10)_ProgramomraadeID(" \
                  f"-10)_SpoersmaalID(-50_-10)_TidID(202212)_TrinnID(10)&format=0&sideNummer=1 "
        url = base_url + filters
        response = requests.get(url)
        df = pd.read_json(response.text)
        # Todo: Check if output has more than one page of results
        return df[["Organisasjonsnummer", "EnhetNavn", "AndelMobbet", "AntallBesvart"]]

    # Choose county
    counties = {'Oslo': '03', 'Rogaland': '11', 'Møre og Romsdal': '15', 'Nordland': '18', 'Viken': '30'
                , 'Innlandet': '34', 'Vestfold og Telemark': '38', 'Agder': '42', 'Vestland': '46'
                , 'Trøndelag': '50', 'Troms og Finnmark': '54'}
    option = st.selectbox('Choose county:', counties.keys())
    st.write('You selected:', option)
    fylke = counties[option]

    # Get data on bullying for all schools in chosen county
    df_bullying = get_bullydata(fylke)

    # Get latitude and longitude for all schools in county, to display on map
    latitudes = {}
    longitudes = {}
    for org in df_bullying["Organisasjonsnummer"]:
        lat, lon = get_coordinates(str(org))
        latitudes[org] = lat
        longitudes[org] = lon

    df_bullying["latitude"] = df_bullying["Organisasjonsnummer"].map(latitudes)
    df_bullying["longitude"] = df_bullying["Organisasjonsnummer"].map(longitudes)

    # Exclude schools with missing latitude or longitude
    df_for_map = df_bullying.loc[(df_bullying["latitude"] > 0) & (df_bullying["longitude"] > 0)]
    df_for_table = df_for_map.iloc[:, 1:4]
    df_for_table.rename(columns={'EnhetNavn': 'School', 'AndelMobbet': 'Percentage of students bullied',
                                 'AntallBesvart': 'Number of students bullied'}, inplace=True)

    # Display data in table format
    st.dataframe(df_for_table)

    # Display data in map format
    # Todo: Change map library to include more functionality in map (e.g. display name of school, different colours)
    st.map(df_for_map)


if __name__ == "__main__":
    main()
