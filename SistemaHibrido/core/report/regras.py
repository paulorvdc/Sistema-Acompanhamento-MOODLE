import datetime

def dia_da_semana(x):
    r = 'Segunda'
    if x == 1:
        r = 'Terça'
    elif x == 2:
        r = 'Quarta'
    elif x == 3:
        r = 'Quinta'
    elif x == 4:
        r = 'Sexta'
    elif x == 5:
        r = 'Sábado'
    elif x == 6:
        r = 'Domingo'
    return r

def nomear_classificacao(x):
    r = 'Risco Intermediário'
    if x == 0:
        r = 'Alto Risco'
    elif x == 2:
        r = 'Sem Risco'
    return r

def saida_rede(x):
    r = 1
    if x < 0.4:
        r = 0
    elif x > 0.6:
        r = 2
    return r

def nomear_rotulo(x):
    if x == 1.0:
        r = 'Ativo'
    elif x == 0.0:
        r = 'Não Ativo'
    else:
        r = x
    return r

def numerar_rotulo(x):
    r = 0
    if x >= 1:
        r = 1
    return r

def create_rotulo(x, datestart, datefinish):
    r = 0
    if x >= datestart and x <= datefinish:
        r = 1
    return r

def regra_t(x):
    r = 0
    if x >= 551:
        r = 1
    else:
        r = 0
    return r

def vet_accuracy(dados):
    vet_accs = []
    for i in range(5):
        k = dados[dados['kmeans'] == i]
        vet_acc = [k['kmeans'].size, k['kmeans'][k['regra'] == 0].size, k['kmeans'][k['regra'] == 1].size]
        vet_accs.append(vet_acc)
    return vet_accs

def cluster_identity(vet_accs):
    cluster_identities = []
    for i in range(len(vet_accs)):
        cluster_id = []
        if vet_accs[i][1] > vet_accs[i][2]:
            cluster_id.append(0)
            cluster_id.append(vet_accs[i][1]/vet_accs[i][0])
            cluster_identities.append(cluster_id)
        else:
            cluster_id.append(1)
            cluster_id.append(vet_accs[i][2]/vet_accs[i][0])
            cluster_identities.append(cluster_id)
    return cluster_identities

def accuracy(cluster_identities, size, vet_accs):
    acc = 0
    for i in range(len(cluster_identities)):
        if cluster_identities[i][0] == 0:
            acc += vet_accs[i][1]
        else:
            acc += vet_accs[i][2]
    return acc / size