#!/usr/bin/env python
# coding: utf-8

# ### Packages required for the webscrapping
#When we visit a web page, our web browser makes a request to a web server.
import requests
#Beautiful Soup is a Python library for pulling data out of HTML and XML files
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time


# ### Get the URLs
#This function helps us create the link for each publication on the page
def url_obt(x):
    # Extract href attribute and paste 'https://urbania.pe' to it.
    #So, we get the URLs of each publication
    return("https://urbania.pe"+x.attrs["href"])   

#With this code we can get all the URLs, dynamically, on the webpage
i=1
#This is an empty list that will contain all the URLs
urls_pag = []
#While let us iterate the process of getting the URLs until it is FALSE
while True :
    #From webpage to webpage, the only change we noticed is  the number of the page. So we need to change the i
    #that respresents  the number of the page.
    #We used the horizontal crawling for getting the URL from the first webpage to the last one.
    urlpag = 'https://urbania.pe/buscar/venta-de-propiedades?page='+str(i)
    #we fetch the content from the url, using the requests library
    resp = requests.get(urlpag)
    ##we use the html parser to parse the url content and store it in a variable.
    soup = BeautifulSoup(resp.text, 'html.parser')
    #We use the tag article and then select its children 'a'. soup.select() returns a list of all possible matches, 
    #so you can easily iterate over it and call each element. This will help us to get the URLs
    etiquetas_a = soup.select('article > a')
    #Every page has publications, when we don´t find any publication. That means the page doesn´t exist and we stop the
    #horizontal scrawling
    if len(etiquetas_a)==0:
        #The break statement terminates the loop containing it
        break
    #'map(url_obt,etiquetas_a)' obtains the href of each element on the list etiquetas_a using the function url_obt.
    #So,we get the URLs of each publication. 
    #'Map' applies a function to all the items in an input_list.
    #Extends list by appending elements from the iterable
    urls_pag.extend(list(map(url_obt,etiquetas_a)))
    #The counter used by while. 
    i = i+1
#urls_pag

#Save the URLs with pandas
#pd.to_pickle(urls_pag, 'urls_pag.pkl')    #to save the dataframe
#urls_pag = pd.read_pickle("urls_pag.pkl")


# ## Get the URL, price in USD, area and coordinates.
#This function will help us when we don´t find a value to consider this as an empty value
def fill_na(fun):
    #If an error is encountered, a try block code execution is stopped and transferred
    #down to the except block. 
    try:
        x = fun('')
    except Exception as e:
        x = ''
    return x


# ### Get the price in USD

#This funtion gets the price in US$ of a property
#We need one parameter, a soup object.
def obtener_precio_dolares(posi_soup):
    try :
        #We select the tag 'div.b-leading-price-property.u-flex-wrap' and all the 'p' tag inside.
        lista_p1 = posi_soup.select_one('div.b-leading-price-property.u-flex-wrap').select('p')
        #We look for '$' in order to find the price in $
        precio_obt = [p.text for p in lista_p1 if p.text.find('$')>0][0]
        #As the structure of the page changes, this step should be considered to generalize the code.
        inicio = precio_obt.find('US$')
        precio_esp = precio_obt[inicio:]
        precio_esp = precio_esp.replace('\n','')
        #Sometimes the price is between parentheses. We want all the prices to have the same format.
        #That is why we must eliminate parentheses.
        precio_1 = precio_esp.replace('(','')
        precio_propiedad = precio_1.replace(')','')
    except:
        precio_propiedad = ''
    return(precio_propiedad)
#We keep the US$, just to show that the price is in dollars.


# ### Get the area
#this function selects the text where the area of the property is indicated
#You need one parameter, a soup object.
#The position of the CSS selector  change, so we consider this code for finding the area.
def obt_posicion_area(posi_soup):
    try :
        #'We select 'div.b-ubication' and then we look for the 'p' tags. Then, we use a 'for' looking for 'm2'. That
        #indicates where the area is stored.
        lista_p = posi_soup.select_one('div.b-ubication').select('p')
        #We get the text where we find the area.
        area_propiedad = [p.text for p in lista_p if p.text.find('m2')>0][0]
    except :
        #When we don´t find 'm2'. That means the publications doesn´t have a value for the area.
        area_propiedad=''
    return(area_propiedad)


# In[37]:
#This function gets the area in the text that contains it.
#The parameter we need is the text where the area is found.
def definir_area(datos_area):
    try :
        #We separate the list into strings, using a white space ' '. Then we look for 'm2' since the previous values indicate the area.
        separados = datos_area.split(' ') 
        #We look for the position of 'm2'.
        find_m2 = separados.index('m2')
        #If 'm2' is in position 1, then the value in position 0 is the area of the property.
        if(find_m2==1):
            area_propiedad = separados[:(find_m2)]
        #If m2 is not in position 1, then: 
        else:
            # If separados[find_m2-2] is equal to '-'. Then, it means that there is a range of areas in the property. 
            if(separados[find_m2-2]=='-'):
                #So the strings are taken considering 3 previous positions to the position of find_m2.
                area_propiedad = separados[(find_m2-3):find_m2]
            #In case the above is not fulfilled, then, only a position prior to m2 is considered.
            else:
                area_propiedad = separados[(find_m2-1)]
        #We join the strings
        area = ''.join(area_propiedad)  
    except :
        #When m2 is not ound, tht means there isn´t a value
        area = ''
    return(area)


# ### Get the coordinates

#This function gets the position of the coordinates
#The parameter we need is the object 'soup'.
def obt_posicion_coor(posi_soup):
    try :
        #We create a list of all the tags 'script' on the page.
        lista_script = posi_soup.select('script')
        #Create a list that contains only the text that has the word 'longitud'.
        #This code was made due to the position of the coordinates varied day by day.
        script = [i.text for i in lista_script if i.text.find('longitud')>0][0]
    except :
        script = ''
    return(script)


#This function gets the longitude of the property
#The parameter you need is the text where the we find the longitude value  
def get_longitud(coordenadas):
    try :
        #coordinates
        #Between these two strings is the value of the longitude.
        #We delete the spaces in the text
        coordenadas = coordenadas.replace(' ','')
        #We get the position where the value longitude is
        inicio_longitud = coordenadas.find('longitud":"')
        inicio_longitud
        fin_longitud = coordenadas.find('",\n\t\t"address"')
        fin_longitud
        #We get the value of longitude
        longitude = coordenadas[inicio_longitud+11:fin_longitud]
    except :
        longitude = ''
    return(longitude)

#This function gets the latitude of the property
#The parameter you need is the text where the we find the latitude value  
def get_latitud(coordenadas):
    try :
        #coordinates
        #Between these two strings is the value of the longitude.
        #We delete the spaces in the text
        coordenadas = coordenadas.replace(' ','')
        #We get the position where the value latitude is
        inicio_latitud=coordenadas.find('latitud":"')
        fin_latitud=coordenadas.find('",\n\t"longitud"')
        fin_latitud
        latitude = coordenadas[inicio_latitud+10:fin_latitud]
    except :
        latitude = ''
    return(latitude)


# ### Get all the data

#An empty list that stores the URL, price, area and coordinates.
lista_datos = []

for information in urls_pag:    
    try:
        #The 'for' gets the information of each publication. We get the URL, price, area and coordinates.
        #From webpage to webpage, the only change we noticed is  the number of the page. So we need to move from page to page
        #in order to get the information of all the publications.    
        resp = requests.get(information)
        print(resp.url)
        #Sometimes the URL in resp.url is different from the one in information, that's why we use this 'if'.
        if resp.url != information :
            #If there is a difference, the code won´t stop. It just will skip to the next URL
            continue
        #create an instance of the BeautifulSoup class to parse our document
        soup = BeautifulSoup(resp.text, 'html.parser')
        # PRICE
        #precio contains the price in dollars
        precio = obtener_precio_dolares(soup)
        
        #AREA
        #We obtain the text that contains area
        posi_area=obt_posicion_area(soup)    
        #We select just the value for the area
        str_area = definir_area(posi_area)
        
        #COORDINATES
        #We get the text that contains the coordinates
        coor = obt_posicion_coor(soup)
        #We get the longitude and latitude
        longi = get_longitud(coor)
        lat = get_latitud(coor)      
        #We store the information in the list 'conjunto'
        conjunto = [resp.url,precio,str_area,longi,lat]        
    except :
        conjunto = []
    #We add the information in the list 'lista_datos'
    lista_datos.append(conjunto)

# ### List with URL, price, area and coordinates.

#We get a list with all the information
#The URL is complete here
#lista_datos

# ### Table with the information
#We make a table with the information
tabla_lista_datos = pd.DataFrame(lista_datos,columns=['URL','Precio','Area','Latitud','Longitud'])
tabla_lista_datos
#We lost the complete URL because it is too long


#Number of properties that doesn´t have a price
sum(tabla_lista_datos['Area']=='')


#Dimensions of the table
tabla_lista_datos.shape


#Number of URLs 
len(urls_pag)

#download the data with .csv format.
tabla_lista_datos.to_csv("webscrapping.csv",sep=";",index=False)