 # -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd 
import re

#PATH FOR THE BROWSER  
PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

driver.get("http://www.buscacep.correios.com.br/sistemas/buscacep/buscaFaixaCep.cfm")

#CHOOSE THE UFs
UFs = ["SC","MG","AM"]

table = {}

#FILLING FORMS
for UF in UFs:

  table[UF] = ""

  select = Select(driver.find_element_by_name('UF'))
  select.select_by_value(UF)
  driver.find_element_by_class_name("btn2.float-right").click()

  flag = 1
  n_pages = 0

  while flag == 1:

    n_pages = n_pages + 1
    
    #GETTING DATA
    if n_pages == 1: 
      dados = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/table[2]")
    else:
      dados = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/table")

    html = dados.get_attribute("innerHTML")
    soup = BeautifulSoup(html, "html.parser")
    table[UF] = table[UF] + str(soup.select_one("tbody"))

    #NEXT TABLE PAGE
    dados = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/div[5]")
    html = dados.get_attribute("innerHTML")
    soup = BeautifulSoup(html, "html.parser")
    next_page = str(soup)

    nextButton = next_page.split()
      
    if nextButton[0] == "<a": 
      driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/div[5]").click()
    else : 
      flag = 0

  else:
    print("DADOS CARREGADOS COM SUCESSO")

#NEW QUERY
  driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/div[6]").click()

#CLOSING BROWSER
driver.quit()

#ARRAY FOR JSON FILE
listaFinal = []

#CLEANING DATA 
jsonString = ""
for UF in UFs:

  localidades = []

  Trs = table[UF].split("<tr")
  contTrs = 0
  contId = 0
  for Tr in Trs:
    if contTrs > 2: 
      contTds = 0
      contId = contId + 1
      local = ""
      faixaCep = ""
      Tds = Tr.split("<td ")
      for Td in Tds:
        if contTds > 0 and contTds < 3 : 
          clean = re.sub("<.*?>", "", "<td "+Td)
          if contTds == 1:
            #LOCALIDADE
            local = clean
          else:
            #FAIXA DE CEP
            faixaCep = clean

#CREATING JSON FILE          
        contTds = contTds + 1
      localidades.append({'id':contId, 'localidade':local, 'faixaDeCep':faixaCep})
      
    contTrs = contTrs + 1

  listaFinal.append({'UF':UF,'localidades':localidades})

listaFinalJson = pd.DataFrame(listaFinal)

listaFinalJson.head()

listaFinalJson.to_json('localidade_CEP.jsonl')