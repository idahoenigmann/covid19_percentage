import csv
import glob
import fire

SORT = 0
EXPORT = True
VERBOSE = True

country_synonyms = []


def add_country_synonym(country_a, country_b):
    found = False

    idx = 0
    for country_list in country_synonyms:
        if country_a in country_list:
            country_synonyms[idx].append(country_b)
            found = True
        elif country_b in country_list:
            country_synonyms[idx].append(country_a)
            found = True
        idx = idx + 1

    if not found:
        country_synonyms.append([country_a, country_b])


def get_data():
    population = dict()
    with open("population.csv", newline='\n') as population_csv:
        reader = csv.reader(population_csv, delimiter=',', quotechar='"')
        for row in reader:
            population[row[0]] = int(row[1])

    for country_list in country_synonyms:
        max_population = 0
        for country in country_list:
            if (country in population) and (max_population < population[country]):
                max_population = population[country]
        for country in country_list:
            population[country] = max_population

    files = list(glob.glob("COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/*.csv"))
    files.sort()
    file = files[-1]

    file_date = file.split("/")[-1].split(".")[0]
    file_date = file_date.split("-")[2] + "-" + file_date.split("-")[0] + "-" + file_date.split("-")[1]

    idx_country_region = 1
    idx_confirmed = 3
    idx_deaths = 4
    idx_recovered = 5

    if file_date >= "2020-03-22":
        idx_country_region = 3
        idx_confirmed = 7
        idx_deaths = 8
        idx_recovered = 9

    with open(file, newline='\n') as csvfile:
        dict_country_cases = dict()

        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(reader)
        for row in reader:
            if row[idx_country_region] in dict_country_cases.keys():
                dict_country_cases[row[idx_country_region]] = [dict_country_cases[row[idx_country_region]][0] +
                                                               int(row[idx_confirmed] if row[idx_confirmed] else 0),
                                                               dict_country_cases[row[idx_country_region]][1] +
                                                               int(row[idx_deaths] if row[idx_deaths] else 0),
                                                               dict_country_cases[row[idx_country_region]][2] +
                                                               int(row[idx_recovered] if row[idx_recovered] else 0)]
            else:
                dict_country_cases[row[idx_country_region]] = [int(row[idx_confirmed] if row[idx_confirmed] else 0),
                                                               int(row[idx_deaths] if row[idx_deaths] else 0),
                                                               int(row[idx_recovered] if row[idx_recovered] else 0)]

    for country in dict_country_cases.keys():
        dict_country_cases[country][0] = dict_country_cases[country][0] - dict_country_cases[country][1] - \
                                         dict_country_cases[country][2]

    return dict_country_cases, population


def filter_data(dict_country_cases, population):
    if VERBOSE:
        print("    {:35s}: {:>10s} {:>10s} {:>10s} {:>10s} {:>10s} {:>10s} {:>10s}\n".format("country", "infected",
                                                                                     "infected %", "deaths", "deaths %",
                                                                                     "recovered", "recovered %",
                                                                                     "population"))

    if EXPORT:
        with open("most_infected.csv", newline='\n', mode='wt') as output_csv:
            output_csv_writer = csv.writer(output_csv)
            output_csv_writer.writerow(["country", "infected", "infected %", "deaths", "deaths %", "recovered",
                                        "recovered %", "population"])

    dcc_sorted = dict()

    for country in dict_country_cases.keys():
        dcc_sorted[country] = [dict_country_cases[country][0],
                               dict_country_cases[country][0] / population[country] * 100
                               if population[country] > 0 else 0,
                               dict_country_cases[country][1],
                               dict_country_cases[country][1] / (dict_country_cases[country][0] +
                                                                 dict_country_cases[country][1] +
                                                                 dict_country_cases[country][2]) * 100
                               if dict_country_cases[country][0] > 0 else 0,
                               dict_country_cases[country][2],
                               (dict_country_cases[country][2] / population[country] * 100)
                               if population[country] > 0 else 0,
                               population[country]]

    dcc_sorted = {k: v for k, v in sorted(dcc_sorted.items(), key=lambda item: item[1][SORT], reverse=True)}

    idx = 1
    for country in dcc_sorted.keys():
        if VERBOSE:
            print("{:>3d}. {:35s}: {:10d} {:10f} {:10d} {:10f} {:10d} {:10f} {:10d}".format(idx, country,
                                                                                     dcc_sorted[country][0],
                                                                                     dcc_sorted[country][1],
                                                                                     dcc_sorted[country][2],
                                                                                     dcc_sorted[country][3],
                                                                                     dcc_sorted[country][4],
                                                                                     dcc_sorted[country][5],
                                                                                     dcc_sorted[country][6]))

        if EXPORT:
            with open("most_infected.csv", newline='\n', mode='a') as output_csv:
                output_csv_writer = csv.writer(output_csv)
                output_csv_writer.writerow([country, dcc_sorted[country][0], dcc_sorted[country][1],
                                            dcc_sorted[country][2], dcc_sorted[country][3],
                                            population[country]])

        idx = idx + 1


def parse_args(verbose=True, sort=0, export=True):
    global SORT
    global EXPORT
    global VERBOSE

    VERBOSE = verbose
    SORT = sort
    EXPORT = export


def main():
    add_country_synonym("DR Congo", "Congo (Kinshasa)")
    add_country_synonym("United States", "US")
    add_country_synonym("Congo", "Congo (Brazzaville)")
    add_country_synonym("Côte d'Ivoire", "Cote d'Ivoire")
    add_country_synonym("Czech Republic (Czechia)", "Czechia")
    add_country_synonym("Other", "Diamond Princess")
    add_country_synonym("South Korea", "Korea, South")
    add_country_synonym("Other", "MS Zaandam")
    add_country_synonym("Saint Kitts & Nevis", "Saint Kitts and Nevis")
    add_country_synonym("St. Vincent & Grenadines", "Saint Vincent and the Grenadines")
    add_country_synonym("Taiwan", "Taiwan*")
    add_country_synonym("Palestinian territories", "West Bank and Gaza")
    add_country_synonym("South Korea", "Republic of Korea")

    dict_country_cases_time, population = get_data()

    filter_data(dict_country_cases_time, population)


if __name__ == "__main__":
    fire.Fire(parse_args)
    main()
