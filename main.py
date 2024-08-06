import pandas as pd
import matplotlib.pyplot as plt

from os import path, listdir


def bva(df, bva_row, sv_list):
    bva_sv_rows = df.loc[df.iloc[:, 7].isin(sv_list)]
    bva_sv_total = bva_sv_rows.iloc[:, 8].sum()
    bva_sv_reg_votes = bva_sv_rows.iloc[:, 17].sum()
    bva_sv_reg_setlakwe = bva_sv_rows.iloc[:, 16].sum()
    bva_sv_reg_isabelle = bva_sv_rows.iloc[:, 15].sum()
    bva_votes = df.iloc[bva_row, 17]
    bva_setlakwe = df.iloc[bva_row, 16]
    bva_isabelle = df.iloc[bva_row, 15]
    total_turnout = bva_sv_reg_votes + bva_votes
    percent_turnout = 100.0 * total_turnout / bva_sv_total
    percent_setlakwe = 100.0 * (bva_sv_reg_setlakwe + bva_setlakwe) / total_turnout
    percent_isabelle = 100.0 * (bva_sv_reg_isabelle + bva_isabelle) / total_turnout
    return {'total_turnout': total_turnout,
            'percent_turnout': percent_turnout,
            'percent_setlakwe': percent_setlakwe,
            'percent_isabelle': percent_isabelle,
            'percent_qc_or_plq': percent_isabelle + percent_setlakwe}


def riding(df, df_riding, idx, csv_name, year=2022):
    df['CSV name'].iloc[idx] = csv_name
    num_rows = df_riding.shape[0]
    num_cols = len(df_riding.columns)
    if year == 2018 and df_riding.columns[-1] != 'B.R.':
        num_cols -= 1  # Spurious last column
    first_party_col = 9
    last_party_col = num_cols - 3  # Last 2 cols are BV and BR
    assert last_party_col > first_party_col  # An election with only one party would be boring
    summary_row = num_rows - 2  # The second-to-last row
    registered_voters = df_riding.iloc[summary_row, 8]
    vote_summary = df_riding.iloc[summary_row, first_party_col:last_party_col + 1]
    vote_summary.sort_values(ascending=False, inplace=True)
    riding_winner_votes = vote_summary[0]
    riding_runner_up_votes = vote_summary[1]
    sum_votes = vote_summary.sum()
    assert sum_votes == df_riding.iloc[summary_row, num_cols-2]
    rejected_votes = df_riding.iloc[summary_row, num_cols-1]
    total_votes = sum_votes + rejected_votes
    caq_col = None
    libs_col = None
    qs_col = None
    pq_col = None
    pcq_col = None
    for i, col_name in enumerate(df_riding.columns):
        if 'C.A.Q.' in col_name:
            assert not caq_col
            caq_col = i
        elif 'P.L.Q.' in col_name:
            assert not libs_col
            libs_col = i
        elif 'Q.S.' in col_name:
            assert not qs_col
            qs_col = i
        elif ' P.Q.' in col_name:
            assert not pq_col
            pq_col = i
        elif year == 2022 and ('P.C.Q.-E.E.D' in col_name or 'P.C.Q-E.E.D.') in col_name:
            assert not pcq_col
            pcq_col = i
    df['registered voters'].iloc[idx] = registered_voters
    df['total votes'].iloc[idx] = total_votes
    df['CAQ votes'].iloc[idx] = df_riding.iloc[summary_row, caq_col]
    df['Liberal votes'].iloc[idx] = df_riding.iloc[summary_row, libs_col]
    df['PQ votes'].iloc[idx] = df_riding.iloc[summary_row, pq_col]
    if year == 2022:
        df['PCQ votes'].iloc[idx] = df_riding.iloc[summary_row, pcq_col]
    df['Riding winner votes'].iloc[idx] = riding_winner_votes
    df['Riding runner-up votes'].iloc[idx] = riding_runner_up_votes
    if 'Camille-Laurin' in csv_name and year == 2022:
        df['QS votes'].iloc[idx] = None
    else:
        df['QS votes'].iloc[idx] = df_riding.iloc[summary_row, qs_col]


def qc2018():
    data_dir = '/home/krzys/Downloads/dge2018'
    file_names = list(filter(lambda s: s.endswith('.csv'), listdir(data_dir)))
    num_ridings = len(file_names)
    col_names = ['CSV name', 'registered voters', 'total votes', 'CAQ votes', 'Liberal votes', 'QS votes', 'PQ votes', 'PCQ votes', 'Riding winner votes', 'Riding runner-up votes']
    df = pd.DataFrame(index=range(num_ridings), columns=col_names)
    for idx, file_name in enumerate(file_names):
        df_riding = pd.read_csv(path.join(data_dir, file_name), encoding='latin-1', sep=';')
        riding(df, df_riding, idx, file_name, year=2018)
    df['% Voter turnout'] = 100.0 * df['total votes'] / df['registered voters']
    df['% Votes for winner'] = 100.0 * df['CAQ votes'] / df['total votes']
    df['% Votes for QS'] = 100.0 * df['QS votes'] / df['total votes']
    df['% Votes for PQ'] = 100.0 * df['PQ votes'] / df['total votes']
    df['% Spread between top two'] = 100.0 * (df['Riding winner votes'] - df['Riding runner-up votes']) / df['total votes']
    return df


def qc(plot=True):
    data_dir = '/home/krzys/Downloads/dge'
    file_names = list(filter(lambda s: s.endswith('.csv'), listdir(data_dir)))
    num_ridings = len(file_names)
    col_names = ['CSV name', 'registered voters', 'total votes', 'CAQ votes', 'Liberal votes', 'QS votes', 'PQ votes', 'PCQ votes', 'Riding winner votes', 'Riding runner-up votes']
    df = pd.DataFrame(index=range(num_ridings), columns=col_names)
    for idx, file_name in enumerate(file_names):
        df_riding = pd.read_csv(path.join(data_dir, file_name), encoding='latin-1', sep=';')
        riding(df, df_riding, idx, file_name)
    df['% Voter turnout'] = 100.0 * df['total votes'] / df['registered voters']
    df['% Votes for winner'] = 100.0 * df['CAQ votes'] / df['total votes']
    df['% Votes for QS'] = 100.0 * df['QS votes'] / df['total votes']
    df['% Votes for PQ'] = 100.0 * df['PQ votes'] / df['total votes']
    df['% Votes for PCQ'] = 100.0 * df['PCQ votes'] / df['total votes']
    df['% Spread between top two'] = 100.0 * (df['Riding winner votes'] - df['Riding runner-up votes']) / df['total votes']

    if plot:
        plt.figure()
        df.plot.scatter('% Voter turnout', '% Votes for winner')
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        plt.title('Votes gagnants vs. taux de participation (province)')
        plt.xlabel('Taux de participation (%)')
        plt.ylabel('Votes pour la CAQ (%)')
        plt.show()

        plt.figure()
        df.plot.scatter('% Voter turnout', '% Votes for QS')
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        plt.title('Voter turnout vs. QS, all ridings')
        plt.show()

        plt.figure()
        df.plot.scatter('% Voter turnout', '% Votes for PQ')
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        plt.title('Voter turnout vs. PQ, all ridings')
        plt.show()

        plt.figure()
        df.plot.scatter('% Voter turnout', '% Votes for PCQ')
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        plt.title('Voter turnout vs. PCQ, all ridings')
        plt.show()

        plt.figure()
        df.plot.scatter('% Spread between top two', '% Voter turnout')
        plt.xlim(100, 0)
        plt.ylim(0, 100)
        plt.title('Voter turnout vs. Spread between top two candidates')
        plt.show()

    return df


# TODO: plot 2022 QS vote %, aggregated by BVA regroupement, vs. same for 2018. Oh but they are diff!
# TODO: fallback: plot SVs for 2022 vs. 2018 (ignore BVA)
def mro2018():
    data_file = 'DGE-80.10_Mont-Royal-Outremont_Sans_SE.csv'
    data_dir = '/home/krzys/Downloads/dge2018'
    df = pd.read_csv(path.join(data_dir, data_file), encoding='latin-1', sep=';')

    # Select only the rows corresponding to regular votes, per SV
    df = df.truncate(after=146)
    voters = df.iloc[:, 8]
    valid_votes = df.iloc[:, 9:17].sum(axis=1)
    qs = df.iloc[:, 16]
    bv = df.iloc[:, 17]
    assert bv.equals(valid_votes)
    br = df.iloc[:, 18]
    all_votes = bv + br

    df['percent_qs'] = 100.0 * qs / all_votes
    return df


def mro(plot=True):
    data_file = 'DGE-80.10_Mont-Royal-Outremont_sans_SE.csv'
    data_dir = '/home/krzys/Downloads'
    df = pd.read_csv(path.join(data_dir, data_file))

    # Count total number of eligible voters
    riding_total = df.iloc[192, 8]
    regr_bvo = df.iloc[147:157, 8]
    regr_bvo_total = regr_bvo.sum()
    hors_qc = df.iloc[190, 8]
    detenus = df.iloc[191, 8]

    # Count total number of actual votes (ignore rows with zero votes)
    riding_votes = df.iloc[192, 17]
    bva_votes = df.iloc[157:185, 17]
    bva_votes_total = bva_votes.sum()
    hebergement_votes = df.iloc[185, 17]
    itinerant_votes = df.iloc[186, 17]
    bds_votes = df.iloc[187, 17]
    hors_circ_votes = df.iloc[189, 17]

    # Advance polling numbers aggregate multiple SVs (ballot boxes): here's an example (BVA1)
    # The number of advance polling votes is significant: 380 vs. 716 regular votes
    # Unfortunately, we don't know how many advance votes came from each SV
    # This precludes a per-SV analysis of voter turnout :(
    # BVA1: SV no 121, 123, 127, 130, 146
    bva1 = bva(df, 157, [121, 123, 127, 130, 146])

    bva2 = bva(df, 158, [117, 125, 140, 142, 145])
    bva3 = bva(df, 159, [122, 131, 132, 144, 147])
    bva4 = bva(df, 160, [124, 126, 128, 134, 136, 138])
    bva5 = bva(df, 161, [36, 119, 137, 139, 141, 143])
    bva6 = bva(df, 162, [37, 120, 129, 133, 135])
    bva7 = bva(df, 163, [101, 103, 105, 107, 111])
    bva8 = bva(df, 164, [68, 100, 102, 104, 110])
    bva9 = bva(df, 165, [65, 71, 106, 112, 114])
    bva10 = bva(df, 166, [67, 108, 109, 115, 118])
    bva11 = bva(df, 167, [66, 69, 70, 113, 116])
    bva12 = bva(df, 168, [12, 16, 34, 53, 55])
    bva13 = bva(df, 169, [9, 14, 19, 22, 54])
    bva14 = bva(df, 170, [11, 18, 21, 23, 27, 29])
    bva15 = bva(df, 171, [8, 10, 26, 30, 33])
    bva16 = bva(df, 172, [13, 17, 20, 25, 31])
    bva17 = bva(df, 173, [15, 24, 28, 32, 35])
    bva18 = bva(df, 174, [2, 5, 6, 40, 44, 48])
    bva19 = bva(df, 175, [3, 7, 39, 41, 45, 46])
    bva20 = bva(df, 176, [1, 4, 38, 42, 43, 47])
    bva21 = bva(df, 177, [80, 81, 83, 87, 89, 97])
    bva22 = bva(df, 178, [85, 91, 93, 95, 99])
    bva23 = bva(df, 179, [82, 86, 92, 96, 98])
    bva24 = bva(df, 180, [79, 84, 88, 90, 94])
    bva25 = bva(df, 181, [49, 58, 62, 75, 78])
    bva26 = bva(df, 182, [50, 57, 61, 64, 73])
    bva27 = bva(df, 183, [51, 59, 63, 72, 76])
    bva28 = bva(df, 184, [52, 56, 60, 74, 77])

    sv_range = range(1, 29, 1)
    df_bva = pd.DataFrame(index=sv_range, columns=['total_turnout', 'percent_turnout', 'percent_setlakwe', 'percent_isabelle', 'percent_qs_or_plq'])
    for bva_num in sv_range:
        d = eval('bva' + str(bva_num))
        i = bva_num - 1
        df_bva.iloc[i] = list(d.values())

    percent_turnout_check = 100.0 * riding_votes / riding_total
    percent_turnout = df_bva['percent_turnout'].sum() / 28.0
    assert abs(percent_turnout - percent_turnout_check) < 3.0

    percent_setlakwe_check = 100.0 * df.iloc[192, 16] / riding_votes
    percent_setlakwe_avg = df_bva['percent_setlakwe'].sum() / 28.0
    assert abs(percent_setlakwe_avg - percent_setlakwe_check) < 2.0

    percent_qs_or_plq = df_bva['percent_qs_or_plq'].sum() / 28.0

    if plot:
        plt.figure()
        df_bva.plot.scatter('percent_turnout', 'percent_setlakwe')
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        plt.title('Voter turnout vs. winner, units aggregated as per BVA group')
        plt.show()

        plt.figure()
        df_bva.plot.scatter('percent_turnout', 'percent_isabelle')
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        plt.title('Voter turnout vs. Isabelle, units aggregated as per BVA group')
        plt.show()

        x = range(0, 101, 1)
        y = []
        for i, _x in enumerate(x):
            y.append(60 - _x)
        plt.figure()
        df_bva.plot.scatter('percent_isabelle', 'percent_setlakwe')
        plt.plot(x, y)
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        plt.xlabel('Votes pour Isabelle (%)')
        plt.ylabel('Votes pour Setlakwe (%)')
        plt.title('Setlakwe vs. Isabelle, BVA+BVO (par regroupement BVA)')
        plt.show()

    # Select only the rows corresponding to regular votes, per SV
    df = df.truncate(after=146)
    voters = df.iloc[:, 8]
    assert riding_total == voters.sum() + regr_bvo_total + hors_qc + detenus
    votes_cast = df.iloc[:, 17]
    assert riding_votes == votes_cast.sum() + bva_votes_total + hebergement_votes + itinerant_votes + bds_votes + hors_circ_votes

    # Plot distribution of winning vote % per SV
    df = df.iloc[:, [9, 10, 11, 15, 16, 17]]
    df['percent_setlakwe'] = 100.0 * df.iloc[:, 4] / df.iloc[:, 5]
    df['percent_isabelle'] = 100.0 * df.iloc[:, 3] / df.iloc[:, 5]
    df['percent_caq'] = 100.0 * df.iloc[:, 2] / df.iloc[:, 5]
    df['percent_pq'] = 100.0 * df.iloc[:, 1] / df.iloc[:, 5]
    df['percent_pcq'] = 100.0 * df.iloc[:, 0] / df.iloc[:, 5]

    lib_ser = df['percent_setlakwe']
    qs_ser = df['percent_isabelle']
    caq_ser = df['percent_caq']
    bins = range(0, 101, 10)

    if plot:
        plt.figure(1)
        lib_ser.plot.hist(bins=bins)
        plt.title('Histogram of winning vote % per unit (SV)')
        plt.xlabel('% votes for Setlakwe')
        plt.ylabel('Number of SVs')

        plt.figure(2)
        qs_ser.plot.hist(bins=bins)
        plt.title('Histogram of winning vote % per unit (SV)')
        plt.xlabel('% votes for Isabelle')
        plt.ylabel('Number of SVs')

        plt.figure(3)
        caq_ser.plot.hist(bins=bins)
        plt.title('Histogram of winning vote % per unit (SV)')
        plt.xlabel('% votes for CAQ')
        plt.ylabel('Number of SVs')

        x = range(0, 101, 1)
        y = []
        for i, _x in enumerate(x):
            y.append(60 - _x)
        plt.figure(4)
        df.plot.scatter('percent_isabelle', 'percent_setlakwe')
        plt.plot(x, y)
        plt.title('Setlakwe vs. Isabelle, par SV (sans BVA)')
        plt.xlabel('Votes pour Isabelle (%)')
        plt.ylabel('Votes pour Setlakwe (%)')
        plt.ylim(0, 100)
        plt.show()

        plt.figure(5)
        df.plot.scatter('percent_caq', 'percent_isabelle')
        plt.plot(x, y)
        plt.title('Isabelle vs. CAQ, per unit (SV)')
        plt.show()

        plt.figure(6)
        df.plot.scatter('percent_pq', 'percent_isabelle')
        plt.plot(x, y)
        plt.title('Isabelle vs. PQ, per unit (SV)')
        plt.show()

        plt.figure(7)
        df.plot.scatter('percent_pcq', 'percent_isabelle')
        plt.plot(x, y)
        plt.show()

    return df


def find_spread(df2018, csv_name):
    hacked_csv_name = csv_name.replace('_sans_', '_Sans_')
    match = df2018.loc[df2018['CSV name'] == hacked_csv_name]
    if match.empty:
        prefix = 'DGE-'
        assert hacked_csv_name.startswith(prefix)
        suffix = hacked_csv_name.split(prefix)[1]
        suffix = suffix.replace('-', '_')
        hacked_csv_name = prefix + suffix
        match = df2018.loc[df2018['CSV name'] == hacked_csv_name]
    if match.empty:
        map_2022_2018 = {
            'DGE-80.10_Gaspé_sans_SE.csv': 'DGE-80.10_Gaspe_Sans_SE.csv',
            'DGE-80-10_Westmount-Saint-Louis_sans_SE.csv': 'DGE-80.10_Westmount-Saint-Louis_Sans_SE.csv',
            'DGE-80.10_Îles-de-la-Madeleine_sans_SE.csv': 'DGE-80.10_Iles-de-la-Madeleine_Sans_SE.csv',
            'DGE-80.10_La_Peltrie_sans_SE.csv': 'DGE-80.10_LaPeltrie_Sans_SE.csv',
            'DGE-80.10_La_Prairie_sans_SE.csv': 'DGE-80.10_LaPrairie_Sans_SE.csv',
            'DGE-80.10_Mégantic_sans_SE.csv': 'DGE-80.10_Megantic_Sans_SE.csv',
            'DGE-80.10_La_Pinière_sans_SE.csv': 'DGE-80.10_LaPiniere_Sans_SE.csv',
            'DGE-80.10_Camille-Laurin_sans_SE.csv': 'DGE-80.10_Bourget_Sans_SE.csv',
            'DGE-80.10_Mille-Îles_sans_SE.csv': 'DGE-80.10_Mille-Iles_Sans_SE.csv',
            'DGE-80.10_Matane-Matapédia_sans-SE.csv': 'DGE-80.10_Matane-Matapedia_Sans_SE.csv',
            'DGE-80-10_Repentigny_sans_SE.csv': 'DGE-80.10_Repentigny_Sans_SE.csv',
            'DGE-80.10_Louis-Hébert_sans_SE.csv': 'DGE-80.10_Louis-Hebert_Sans_SE.csv',
            'DGE-80.10_Jonquière_sans_SE.csv': 'DGE-80.10_Jonquiere_Sans_SE.csv',
            'DGE-80.10_Lévis_sans_SE.csv': 'DGE-80.10_Levis_Sans_SE.csv',
            'DGE-80.10_Maskinongé_sans_SE.csv': 'DGE-80.10_Maskinonge_Sans_SE.csv',
            'DGE-80.10_Côte-du-Sud_sans_SE.csv': 'DGE-80.10_Cote-du-Sud_Sans_SE.csv',
            'DGE-80.10_Nicolet-Bécancour_sans_SE.csv': 'DGE-80.10_Nicolet-Becancour_Sans_SE.csv',
            'DGE-80.10_Les_Plaines_sans_SE.csv': 'DGE-80.10_LesPlaines_Sans_SE.csv',
            'DGE-80.10_D\'Arcy-McGee_sans_SE.csv': 'DGE-80.10_DArcy-McGee_Sans_SE.csv',
            'DGE-80.10_Lotbinière-Frontenac_sans_SE.csv': 'DGE-80.10_Lotbiniere-Frontenac_Sans_SE.csv',
            'DGE-80.10_L\'Assomption_sans_SE.csv': 'DGE-80.10_LAssomption_Sans_SE.csv',
            'DGE-80.10_Prévost_sans_SE.csv': 'DGE-80.10_Prevost_Sans_SE.csv',
            'DGE-80.10_Notre-Dame-de-Grâce_sans_SE.csv': 'DGE-80.10_Notre-Dame-de-Grace_Sans_SE.csv'

        }
        if csv_name in map_2022_2018:
            hacked_csv_name = map_2022_2018[csv_name]
            match = df2018.loc[df2018['CSV name'] == hacked_csv_name]
    if not match.empty:
        spread = match[match.columns[-1]].item()
        return spread
    return None


if __name__ == '__main__':
    df_mro2022 = mro(plot=False)
    df_mro2018 = mro2018()

    df_mro2022['percent_qs_2018'] = df_mro2018['percent_qs']

    x = range(0, 51, 1)
    y = x

    plt.figure()
    df_mro2022.plot.scatter('percent_isabelle', 'percent_qs_2018')
    plt.plot(x, y)
    plt.title('QS 2022 vs. 2018')
    plt.show()

    diff_ser = df_mro2022['percent_isabelle'] - df_mro2022['percent_qs_2018']
    bins = range(-50, 50, 10)

    plt.figure()
    diff_ser.plot.hist(bins=bins)
    plt.title('% vote for QS 2022 vs. 2018, per SV')
    plt.xlabel('2022 minus 2018 (%)')
    plt.ylabel('Number of SVs')
    plt.show()

    avg_increase = diff_ser.sum() / len(diff_ser)

    df = qc(plot=False)
    df2018 = qc2018()

    spread_2018 = pd.Series(index=df.index)
    for i, row in df.iterrows():
        csv_name = df.iloc[i, 0]
        spread_2018[i] = find_spread(df2018, csv_name)

    df['% Spread between top two in 2018'] = spread_2018
    plt.figure()
    df.plot.scatter('% Spread between top two in 2018', '% Voter turnout')
    plt.xlim(70, 0)
    plt.ylim(0, 100)
    plt.xlabel('L\'écart entre le gagnant et le 2e en 2018 (%)')
    plt.ylabel('Taux de participation (%)')
    plt.title('Taux de participation 2022 vs. compétitivité en 2018')
    plt.show()

    x = range(0, 101, 1)
    y = x
    plt.figure()
    df.plot.scatter('% Spread between top two', '% Spread between top two in 2018')
    plt.plot(x, y)
    plt.xlim(70, 0)
    plt.ylim(70, 0)
    plt.title('Tightness of race: 2022 vs. 2018')
    plt.show()

    df['% Spread between top two, 2022+2018 avg'] = (df['% Spread between top two'] + df['% Spread between top two in 2018']) / 2
    plt.figure()
    df.plot.scatter('% Spread between top two, 2022+2018 avg', '% Voter turnout')
    plt.xlim(60, 0)
    plt.ylim(0, 100)
    plt.title('Tightness of race (2022 + 2018 avg) vs. Voter turnout')
    plt.show()

    pass
