import random
import re
import numpy as np
import pandas as pd
abeceda = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ' ']

# Preberi frekvenčno tabelo
def preberi_frekv_tabelo(name):
    f = open(f"{name}order.txt", "r")
    input_txt = (f.read())
    split_txt = input_txt.split("\n")
    pop_txt = []
    for i in range(3, len(split_txt)):
        txt = split_txt[i]
        pop_txt.append(txt.split("||")[-1])
    arr = np.fromstring("\n".join(pop_txt), sep=" ")
    arr[arr == 0] = 1e-6
    return arr

exp_freq = [preberi_frekv_tabelo("i"), preberi_frekv_tabelo("ii"), preberi_frekv_tabelo("iii")]
nicle_arr = [np.zeros(pow(27,1)), np.zeros(pow(27,2)), np.zeros(pow(27,3))]
# Naredi prevajalnik
def postavi_kljuc(list):
    dict = {}
    for index, element in enumerate(abeceda):
        dict[ord(element)] = list[index]
    return dict


def count_differences(string1, string2):
    razlike = 0
    for i in range(len(string1)):
        if string1[i] != string2[i]:
            razlike += 1
    return razlike


abeceda_ind_dict = {}
stevila = range(0, len(abeceda) + 1)
for index, element in enumerate(abeceda):
    abeceda_ind_dict[element] = stevila[index]

# Pretvori niz znakov v številko, ki predstavlja indeks v frekvenčni tabeli
def letter_to_index(letter_arr):
    ind_list = []
    for word in letter_arr:
        if len(letter_to_ind_dict) == 20439:
            ind = letter_to_ind_dict[word]
        else:
            ind = 0
            for i in range(1, len(word) + 1):
                ind +=  pow(27, i-1)  * abeceda_ind_dict[word[-i]]
        ind_list.append(ind)
    return np.array(ind_list)

# Razdeli besedilo na n-znakovne nize - če je n>1 naredi tudi to na zamaknjenem besedilu
def split_txt(txt, n):
    txt_list = []
    for i in range(n):
        txt_list.append(txt)
        txt = txt[i+1:]
    split_txt_list = []
    for i in range(len(txt_list)):
        for j in range(int(len(txt_list[i])/n)):
            mesto = j * n
            split_txt_list.append(txt_list[i][mesto : mesto + n])
    return(np.array(split_txt_list))

# podaj oceno prevoda na podlagi pričakovanih frekvenc
def oceni_prevod(txt):
    txt_splits = [split_txt(txt, i) for i in [1, 2, 3]]
    score = []
    for i in range(3): 
        unq = np.unique(txt_splits[i], return_counts=True)
        indeksi = letter_to_index(unq[0])
        act_freq = nicle_arr[i].copy()
        act_freq[indeksi] += (unq[1]/int(len(txt)/(i+1)))
        test = act_freq * np.log(exp_freq[i])
        score.append(np.sum(act_freq * np.log(exp_freq[i])))
    return(sum(score))

# Najdi začetni ključ - na podlagi najpogostejših znakov v angleščini
def zacetni_kljuc(txt):
    crke = np.unique(split_txt(txt, 1), return_counts=True)
    values = nicle_arr[0].copy()
    values[letter_to_index(crke[0])] += crke[1]
    sorted_df = pd.DataFrame({"a" : abeceda, "b" : values}).sort_values("b",0, ascending=False)
    urejene_crke = sorted_df["a"].values.tolist()
    urejene_exp = pd.DataFrame({ "a": abeceda,"b" : exp_freq[0]}).sort_values("b",0, ascending=False)["a"].values.tolist()
    dict = {val : urejene_exp[i] for i, val in enumerate(urejene_crke)}
    return [dict[crka] for crka in abeceda]

letter_to_ind_dict = {}
for crka1 in abeceda:
    letter_to_ind_dict[crka1] = int(letter_to_index([crka1]))
    for crka2 in abeceda:
        beseda2 = crka1 + crka2
        letter_to_ind_dict[beseda2] = int(letter_to_index([beseda2]))
        for crka3 in abeceda:
            beseda3 = beseda2 + crka3
            letter_to_ind_dict[beseda3] = int(letter_to_index([beseda3]))

f = open("input.txt", "r")
input_txt = (f.read())
filtriran_txt = "".join(re.findall("[a-z]| |\n", input_txt.lower()))
filtriran_txt = filtriran_txt.replace("\n", " ")

ponovitve = 1
mcmc_iter = [100, 500, 1000, 2000, 3000, 5000]
#mcmc_iter = [1000]
changes = 2
rezultati =np.zeros((ponovitve, len(mcmc_iter)))
rezultati2 = []


for k, iter_n in enumerate(mcmc_iter):
    for j in range(ponovitve):
        random_abc = abeceda.copy()

        random.shuffle(random_abc)

        kljuc = postavi_kljuc(random_abc)
        zakodiran_txt = filtriran_txt.translate(kljuc)


        poskus_random_abc0 = zacetni_kljuc(zakodiran_txt)
        poskus_txt = zakodiran_txt.translate(postavi_kljuc(poskus_random_abc0) )
        ocena0 = oceni_prevod(poskus_txt)
        for i in range(iter_n):
            poskus_random_abc1 = poskus_random_abc0.copy()
            indeksi = random.sample(range(27), changes)
            urejeni_ind = sorted(indeksi)
            while urejeni_ind == indeksi:
                random.shuffle(indeksi)
            for l in range(changes):
                poskus_random_abc1[urejeni_ind[l]] = poskus_random_abc0[indeksi[l]]

            poskus_kljuca = postavi_kljuc(poskus_random_abc1)
            poskus_txt = zakodiran_txt.translate(poskus_kljuca)
            ocena1 = oceni_prevod(poskus_txt)

            if ocena0 < ocena1:
                alpha = np.exp(ocena0 - ocena1)
                stoh_komp = random.random()
                if stoh_komp < alpha:
                    poskus_random_abc0 = poskus_random_abc1
                    ocena0 = ocena1
            if ponovitve == 1:
                rezultati2.append(ocena0)
        nov_kljuc = postavi_kljuc(poskus_random_abc0)
        prevod_abc = "".join(abeceda).translate(kljuc).translate(nov_kljuc)
        natancnost = 1 - count_differences("".join(abeceda),prevod_abc)/27
        rezultati[j,k] = natancnost
        if ponovitve == 1:
            pd.DataFrame(np.array(rezultati2)).to_csv("DN5_ena_sim.csv")
            prevod_abc_org = [crka.translate(kljuc) for crka in abeceda]
            prevod_abc_nov = [crka.translate(nov_kljuc) for crka in prevod_abc_org]
            pd.DataFrame({"abc" : abeceda,  "nov_kljuc" : prevod_abc_nov}).to_csv("DN5_prevod.csv")
rezultati_df = pd.DataFrame(rezultati, columns=mcmc_iter)
rezultati_df.to_csv("DN5_sim_result.csv")
print()