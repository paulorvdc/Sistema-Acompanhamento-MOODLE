#!/bin/bash
source <caminho virtual env se necessario>
cd <caminho da pasta onde se encontram o codigo da api drive>
python api_drive.py download
unzip banco.zip
cd tmp
cat *.sql > banco.sql
mysql -u root --password="<senha mysql>" -e 'CREATE DATABASE <database mysql>;'
mysql -u root --password="<senha mysql>" nead < banco.sql
cd ..
python sqlToMongo.py
mysql -u root --password="<senha mysql>" -e 'DROP DATABASE <database mysql>;'
rm banco.zip
rm -rf tmp
echo "loaded data: `date`" >> log_manutencao.txt
