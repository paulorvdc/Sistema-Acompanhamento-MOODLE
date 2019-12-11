# Sistema-Acompanhamento-MOODLE
Sistema que permite acompanhamento de usuários da plataforma MOODLE, com módulos preditivos e de geração de gráficos. Versão open source inicial, em breve seguirá versão com tutorial de instalação, de uso e módulo para monitorar uso do próprio sistema. 

Este Sistema é desenvolvido em conjunto com Alan Henschel Costa (https://github.com/alanhenschel) e está também disponivel no repositório dele.

Durante o processo de desenvolvimento desse sistema foram publicados alguns trabalhos que trazem conceitos importantes para explicar o que está ocorrendo, sendo eles dois artigos de TCC: <https://drive.google.com/file/d/1xHYporplgKmSzFvQL2vpbMABHDMq1yJw/view> e <https://drive.google.com/file/d/1TWNVQUrQEvjuaCIDmTjBh5j2Zrrb7nHu/view>

## Installation 

Para instalar esse sistema web, você vai precisar do Python 3.x e de algumas bibliotecas. Para instalar estas bibliotecas é possível rodar os seguintes comandos: 
```
pip install django
pip install pymongo
pip install djongo
pip install numpy
pip install pandas
pip install scikit-learn
pip install tensorflow
pip install keras
``` 
Com o ambiente Python configurado agora é necessário instalar o MongoServer e criar uma collection com o nome `SistemaHibrido`. Quanto a configuração do MongoDB com o sistema existem duas opções: (i) criar o usuário e senha para o MongoDB; ou (ii) utilizar um server Mongo sem autenticação e retirar todos os trechos de autenticação presentes no código em Python.

Após essas configurações é possível iniciar o sistema pela primeira para checar alguns erros referentes a esse processo da instalação. Para isso acesse o diretório principal do `SistemaHibrido` e rode os seguintes comandos:
```
python manage.py migrate
python manage.py runserver
```

Continuação do tutorial de instalação em novas versões...
