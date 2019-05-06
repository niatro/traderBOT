###############################################################################
# #####   ESTAS CLASES OBTIENEN LAS MATRICES DE ESTADO INICIAL S Y  DE    #####
# ##### PROBABILIDADES S PARA ESTADOS DEFINIDOS COMO T, t, o y O
##############################################################################
# %% Modulos externos
from api_cc_hltc import CryptoConector
import numpy as np

# %% Funcciones


def matriz_1D_rend_diario(lapso, token, fiat):
    df = CryptoConector(lapso, token, fiat)
    hltc = df.precioDia()
    # CAMBIA EL INDICE DEL PANDA AL CAMPO TIME
    hltc.set_index('time', inplace=True)

    # BOTA LAS COLUMNAS DE VOLUMENES
    hltc.drop(['volumeto', 'volumefrom'], axis=1, inplace=True)

    # OBTENGO LAS MEDIAS PARA CADA DIA PROMEDIANDO LA MAXIMA, LA MINIMA,  APE
    # RTURA Y PRECIO DE CIERRE PARA CADA RANGO DE TIEMPO ESTO EN EL EJE HORIZON
    hltc = hltc.mean(axis=1, skipna=True)

    # TRANSFORMA EL PANDA --> NUMPY CON LA FUNCION values
    # MATRIZ UNIDIMENCIONAL DE 1 X N
    hltc = hltc.values

    # SE CALCULA EL RENDIMIENTO CORTANDO LOS NUMPY COMO SI FUERAN STRINGS SE <
    # SU DIMENCION EN UNO
    rend = (hltc[1:] - hltc[:-1]) / hltc[1:]
    np.set_printoptions(precision=5, suppress=True,)
    return rend


def matriz_1D_rend_hora(lapso, token, fiat):
    df = CryptoConector(lapso, token, fiat)
    hltc = df.precioHora()
    # CAMBIA EL INDICE DEL PANDA AL CAMPO TIME
    hltc.set_index('time', inplace=True)

    # BOTA LAS COLUMNAS DE VOLUMENES
    hltc.drop(['volumeto', 'volumefrom'], axis=1, inplace=True)

    # OBTENGO LAS MEDIAS PARA CADA DIA PROMEDIANDO LA MAXIMA, LA MINIMA,  APE
    # RTURA Y PRECIO DE CIERRE PARA CADA RANGO DE TIEMPO ESTO EN EL EJE HORIZON
    hltc = hltc.mean(axis=1, skipna=True)

    # TRANSFORMA EL PANDA --> NUMPY CON LA FUNCION values
    # MATRIZ UNIDIMENCIONAL DE 1 X N
    hltc = hltc.values

    # SE CALCULA EL RENDIMIENTO CORTANDO LOS NUMPY COMO SI FUERAN STRINGS SE <
    # SU DIMENCION EN UNO
    rend = (hltc[1:] - hltc[:-1]) / hltc[1:]
    np.set_printoptions(precision=5, suppress=True,)
    return rend


def str_TOto_lap_1H(lapso, token, fiat):
    """ Esta funcion clasifica el numpy que entra por la funcion
    matriz_1D_rend_hora y la transforma en un string donde cada caracter repres
    enta un estado
    """
    rend = matriz_1D_rend_hora(lapso, token, fiat)
    std = rend.std()
    mis_estados = ''
    for i in rend:
        if i > std:
            mis_estados = mis_estados + 'T'
        elif i > 0 and i <= std:
            mis_estados = mis_estados + 't'
        elif i <= 0 and i >= std * -1:
            mis_estados = mis_estados + 'o'
        else:
            mis_estados = mis_estados + 'O'
    return mis_estados


def str_TOto_lap_1D(lapso, token, fiat):
    """ Esta funcion clasifica el numpy que entra por la funcion
    matriz_1D_rend_hora y la transforma en un string donde cada caracter repres
    enta un estado
    """
    rend = matriz_1D_rend_diario(lapso, token, fiat)
    std = rend.std()
    mis_estados = ''
    for i in rend:
        if i > std:
            mis_estados = mis_estados + 'T'
        elif i > 0 and i <= std:
            mis_estados = mis_estados + 't'
        elif i <= 0 and i >= std * -1:
            mis_estados = mis_estados + 'o'
        else:
            mis_estados = mis_estados + 'O'
    return mis_estados


def div0(a, b):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide(a, b)
        c[~ np.isfinite(c)] = 0  # -inf inf NaN
    return c


def dic_frec_tran(cadena):
    list = 'TtoO'
    dicc = {}
    for indice in range(len(cadena) - 1):
        fase_B = cadena[indice:indice + 3:1]
        for fase_1_A in list:
            for fase_2_A in list:
                for fase_3_A in list:
                    fase_acumuladora = fase_1_A + fase_2_A + fase_3_A
                    if fase_B == fase_acumuladora:
                        if fase_B in dicc:
                            cont = dicc[fase_B] + 1
                            dicc.update({fase_B:  cont})
                        else:
                            dicc.update({fase_B:  1})
                    elif fase_acumuladora not in dicc:
                        dicc.update({fase_acumuladora:  0})
    return(dicc)

# %% Objetos


class Markov_X():
    def __init__(self, hora_o_dia, lapso, lapso_s, token, fiat):
        self.lapso = lapso
        self.token = token
        self.fiat = fiat
        self.est_totales = 16
        self.est_transf = 4
        self.lapso_s = lapso_s
        if hora_o_dia == 'hora':
            self.el_dicc_de_frec = dic_frec_tran(
                str_TOto_lap_1H(self.lapso, self.token, self.fiat))
            self.cadena_estados = str_TOto_lap_1H(
                self.lapso, self.token, self.fiat)
        elif hora_o_dia == 'dia':
            self.el_dicc_de_frec = dic_frec_tran(
                str_TOto_lap_1D(self.lapso, self.token, self.fiat))
            self.cadena_estados = str_TOto_lap_1D(
                self.lapso, self.token, self.fiat)

    def imprimir(self):
        print(self.lapso)

    def dic_frecuencias(self):
        return self.el_dicc_de_frec

    def str_de_est(self):
        return self.cadena_estados

    def matriz_P(self):
        """Transforma un diccionario en una lista y luego en un ARRAY
        lo dimenciona para que sea simetrico y considerando el total de estados
        llena con ceros y foma la matriz de transicion
        """

        array_1D = np.array(list(self.el_dicc_de_frec.values()))
        array_2D = array_1D.flatten().reshape(
            self.est_totales, self.est_transf)
        array_2D_sim = np.pad(
            array_2D, ((0, 0), (0, self.est_totales -
                                self.est_transf)), mode='constant')
        for i in range(self.est_totales):
            if i % 4 == 0:
                array_2D_sim[i] = np.roll(array_2D_sim[i], 0)
            elif i % 4 == 1:
                array_2D_sim[i] = np.roll(array_2D_sim[i], 4)
            elif i % 4 == 2:
                array_2D_sim[i] = np.roll(array_2D_sim[i], 8)
            elif i % 4 == 3:
                array_2D_sim[i] = np.roll(array_2D_sim[i], 12)
        array_sum = np.sum(array_2D_sim, axis=1, keepdims=True)
        array_P = div0(array_2D_sim, array_sum)
        np.set_printoptions(precision=3)
        return array_P

    def matriz_S(self):
        len_datos_s = self.lapso_s
        largo_cadena = len(self.cadena_estados[-len_datos_s:])
        dic_est = {'TT': 0, 'Tt': 0, 'To': 0, 'TO': 0,
                   'tT': 0, 'tt': 0, 'to': 0, 'tO': 0,
                   'oT': 0, 'ot': 0, 'oo': 0, 'oO': 0,
                   'OT': 0, 'Ot': 0, 'Oo': 0, 'OO': 0}
        for i in range(largo_cadena):
            # print(cadena_estados[i-1:i+1])
            if self.cadena_estados[i - 1:i + 1] == 'TT':
                dic_est['TT'] = dic_est['TT'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'Tt':
                dic_est['Tt'] = dic_est['Tt'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'To':
                dic_est['To'] = dic_est['To'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'TO':
                dic_est['TO'] = dic_est['TO'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'tT':
                dic_est['tT'] = dic_est['tT'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'tt':
                dic_est['tt'] = dic_est['tt'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'to':
                dic_est['to'] = dic_est['to'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'tO':
                dic_est['tO'] = dic_est['tO'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'oT':
                dic_est['oT'] = dic_est['oT'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'ot':
                dic_est['ot'] = dic_est['ot'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'oo':
                dic_est['oo'] = dic_est['oo'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'oO':
                dic_est['oO'] = dic_est['oO'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'OT':
                dic_est['OT'] = dic_est['OT'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'Ot':
                dic_est['Ot'] = dic_est['Ot'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'Oo':
                dic_est['Oo'] = dic_est['Oo'] + 1
            elif self.cadena_estados[i - 1:i + 1] == 'OO':
                dic_est['OO'] = dic_est['OO'] + 1
        # print(dic_est)
        array_1D = np.array(list(dic_est.values()))
        array_2D = array_1D.flatten().reshape(1, 16)
        array_S = div0(array_2D, array_2D.sum())
        return array_S


class Prediccion():
    def __init__(self, forward, str_estados, matriz_S, matriz_P):
        self.forward = forward
        self.str_estados = str_estados
        self.matriz_S = matriz_S
        self.matriz_P = matriz_P

    def matriz_S_n(self):
        matriz_res = self.matriz_S
        for i in range(self.forward):
            matriz_res = np.dot(matriz_res, self.matriz_P)
            # matriz_res = np.dot(matriz_res, self.matriz_P)
        return matriz_res

# %% Codigo


if __name__ == '__main__':
    nano = Markov_X('hora', 1000, 50, 'XRP', 'USD')
    print('Estados')
    print(nano.str_de_est())
    print('Frecuencias')
    print(nano.dic_frecuencias())
    print('Matriz S')
    print(nano.matriz_S())
    print('Matriz P')
    print(nano.matriz_P())

    print('Matriz S a n')

    augur = Prediccion(10, nano.str_de_est(), nano.matriz_S(), nano.matriz_P())

    print(augur.matriz_S_n())
