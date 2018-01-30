#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  libSIIAU.py
#  
#  Copyright 2017 ImNotRoot <https://github.com/ImNotRoot>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

#from commands import getoutput, getstatusoutput
from requests import get, post

import sys, time, os

class AuthenticationError(BaseException):
    def __init__(self, message):
        self.message = message
        super(AuthenticationError, self).__init__(message)

class Alumno:
	__UA="User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36"
	__URL="http://siiauescolar.siiau.udg.mx"
	
	__headers = {
		'User-Agent': __UA,
	}
	
	__COOKIES=""
	__majrp=""
	
	codigo=""
	nip=""
	nombre=""
	items=[]
	carreras=[]
	valido=True
	
	pidm=""
	
	def __getCarreras(self,url):
		#cmd="curl -L -b cookies.txt -i -A '"+self.__UA+"' -X GET '"+self.__URL+""+url+"'"
		r=get(self.__URL+""+url,headers=self.__headers,cookies=self.__COOKIES)
		#out=getoutput(cmd)
		out=r.text
		if("OPTION" in out):
			cab='<OPTION value="'
			while(cab in out):
				temp=""
				val1=""
				val2=""
				out=out[out.find(cab)+len(cab):]
				temp=out[:out.find('"')]
				val1=temp[:temp.find("-")]
				val2=temp[temp.find("-")+1:]
				temp={"carrera":val1,"inicio":val2}
				self.items.append(temp)
		else:
			self.items.append(None)
		self.__getInfoBasica()
	
	def __getLink(self):
		#cmd="curl -L -b cookies.txt -i -A '"+self.__UA+"' -X GET siiauescolar.siiau.udg.mx/wus/gupmenug.menu_sistema?p_pidm_n="+str(self.pidm)
		r=get("http://siiauescolar.siiau.udg.mx/wus/gupmenug.menu_sistema?p_pidm_n="+str(self.pidm),headers=self.__headers,cookies=self.__COOKIES)
		out=r.text
		#out=getoutput(cmd)
		grado=""
		flag=True
		cab='<img src="/ows-img/closed.gif" alt="'
		cab2='<a href="'
		while(cab in out and flag):
			out=out[out.find(cab)+len(cab):]
			grado=out[:out.find('"')]
			out=out[out.find(cab2)+len(cab2):]
			link=out[:out.find('"')]
			#print link
			if(" " not in link):
				#print link
				flag=False
				self.__getCarreras(link)
		if(flag):
			self.items.append(None)
			self.__getInfoBasica();
			#print "Por el momento el API no soporta la extracción de datos para alumnos solamente con preparatoria"
	
	def __getPidm(self,text):
		cab='p_bienvenida_c" VALUE="'
		text=text[text.find(cab)+len(cab):]
		text=text[:text.find('"')]
		self.pidm=text
		#print text
	
	def __getInfoBasica(self):
		encuesta=False
		for info in self.items:
			if(info==None):
				#cmd="curl -L -b cookies.txt -i -A '"+self.__UA+"' -X GET 'siiauescolar.siiau.udg.mx/wal/sgphist.ficha?pidmp="+self.pidm+"'"
				r=get("http://siiauescolar.siiau.udg.mx/wal/sgphist.promedio?pidmp="+self.pidm,headers=self.__headers,cookies=self.__COOKIES)
			else:
				#cmd="curl -L -b cookies.txt -i -A '"+self.__UA+"' -X GET 'siiauescolar.siiau.udg.mx/wal/sgphist.ficha?pidmp="+self.pidm+"&majrp="+info["carrera"]+"&cicloap="+info["inicio"]+"'"
				r=get("http://siiauescolar.siiau.udg.mx/wal/sgphist.promedio?pidmp="+self.pidm+"&majrp="+info["carrera"]+"&cicloap="+info["inicio"],headers=self.__headers,cookies=self.__COOKIES)
			#out=getoutput(cmd)
			out=r.text
			if("Encuestas</b>" in out):
				encuesta=True
				#print("Favor de contestar todas las encuestas para poder continuar")
			else:
				#print out
				out=out[out.find("Nombre:"):]
				out=out[out.find("<FONT"):]
				out=out[out.find(">")+1:]
				self.nombre=out[:out.find("</FONT>")]
				
				out=out[out.find("Situaci"):]
				out=out[out.find("<FONT"):]
				out=out[out.find(">")+1:]
				situacion=out[:out.find("</FONT>")]
				
				out=out[out.find("Carrera:"):]
				out=out[out.find("<FONT"):]
				out=out[out.find(">")+1:]
				carrera=out[:out.find("</FONT>")]
				
				self.__majrp=carrera[carrera.find("(")+1:carrera.find(")")]
				
				out=out[out.find("Centro:"):]
				out=out[out.find("<FONT"):]
				out=out[out.find(">")+1:]
				centro=out[:out.find("</FONT>")]
				
				out=out[out.find("Sede:"):]
				out=out[out.find("<FONT"):]
				out=out[out.find(">")+1:]
				sede=out[:out.find("</FONT>")]
				
				out=out[out.find("PROMEDIO"):]
				out=out[out.find("<FONT"):]
				out=out[out.find(">")+1:]
				promedio=out[:out.find("</FONT>")]
				
				self.carreras.append({"carrera":carrera,"centro":centro,"sede":sede,"situacion":situacion,"promedio":promedio})
		#print self.carreras
		if(not encuesta):
			self.__getKardex()
		
	def __getKardex(self):
		cont=0
		encuesta=False
		for info in self.items:
			if(info == None):
				r=get("http://siiauescolar.siiau.udg.mx/wal/sgphist.kardex?pidmp="+self.pidm+"&majrp="+self.__majrp,headers=self.__headers,cookies=self.__COOKIES)
			else:
				#r=get("http://siiauescolar.siiau.udg.mx/wal/sgphist.kardex?pidmp=891060&majrp=INNI&cicloap=201420",cookies=self.__COOKIES)
				r=get("http://siiauescolar.siiau.udg.mx/wal/sgphist.kardex?pidmp="+self.pidm+"&majrp="+info["carrera"]+"&cicloap="+info["inicio"],headers=self.__headers,cookies=self.__COOKIES)
			out=r.text
			materias=[]
			if("Encuestas</b>" in out):
				encuesta=True
				#print("Favor de contestar todas las encuestas para poder continuar")
			else:
				'''
				cab="Calendario "
				cab2="</FONT>"
				'''
				
				cab='<TR bgcolor="#ffffff">'
				cab2="<A HREF="
				cab3="<FONT "
				cab4='<TD COLSPAN="3"></TD>'
				#print out
				while(cab in out):
					out=out[out.find(cab)+len(cab):]
					aprobado=True
					#print out.find(cab4)
					if(out.find(cab4)!=1):
						out=out[out.find(cab2)+len(cab2):]
						out=out[out.find(">")+1:]
						nrc=out[:out.find("</A>")]
						
						out=out[out.find(cab2)+len(cab2):]
						out=out[out.find(">")+1:]
						clave=out[:out.find("</A>")]
						
						out=out[out.find(cab3)+len(cab3):]
						out=out[out.find(">")+1:]
						materia=out[:out.find("</FONT>")]
					
					out=out[out.find(cab3)+len(cab3):]
					if(out.find('COLOR="red"')==0):
						aprobado=False
						#print "reprobado"
					out=out[out.find(">")+1:]
					calificacion=out[:out.find("</FONT>")]
					
					out=out[out.find(cab3)+len(cab3):]
					out=out[out.find(">")+1:]
					tipo=out[:out.find("</FONT>")]
					
					out=out[out.find(cab3)+len(cab3):]
					out=out[out.find(">")+1:]
					nc=out[:out.find("</FONT>")]
					
					out=out[out.find(cab3)+len(cab3):]
					out=out[out.find(">")+1:]
					fecha=out[:out.find("</FONT>")]
					
					materias.append({"nrc":nrc,"clave":clave,"materia":materia,"calificacion":calificacion,"aprobado":aprobado,"tipo":tipo,"nc":nc,"fecha":fecha})
					#print nrc,clave,materia,calificacion,tipo,nc,fecha
					'''
					out=out[out.find(cab):]
					print out[:out.find(cab2)]
					out=out[out.find(cab2)+len(cab2):]
					'''
			self.carreras[cont]["kardex"]=materias
			cont=cont+1
		if(not encuesta):
			self.__getActuales()
		#print self.carreras
	
	def __getActuales(self):
		cont=0
		encuesta=False
		for info in self.items:
			if(info == None):
				r=get("http://siiauescolar.siiau.udg.mx/wal/sgpregi.horario?pidmp="+self.pidm+"&majrp="+self.__majrp,headers=self.__headers,cookies=self.__COOKIES)
			else:
				#r=get("http://siiauescolar.siiau.udg.mx/wal/sgphist.kardex?pidmp=891060&majrp=INNI&cicloap=201420",cookies=self.__COOKIES)
				r=get("http://siiauescolar.siiau.udg.mx/wal/sgpregi.horario?pidmp="+self.pidm+"&majrp="+info["carrera"],headers=self.__headers,cookies=self.__COOKIES)
			out=r.text
			#print out
			if("Encuestas</b>" in out):
				encuesta=True
				#print("Favor de contestar todas las encuestas para poder continuar")
			else:
				#print out
				cab='<SELECT NAME="pCiclo"'
				if(cab in out):
					out=out[out.find(cab)+len(cab):]
					cab=" value='"
					out=out[out.find(cab)+len(cab):]
					ciclo=out[:out.find("'")]
					params={"pidmP":self.pidm,"cicloP":ciclo,"encaP":"0"}
					if(info!=None):
						params["majrP"]=info["carrera"]
					else:
						params["majrP"]=self.__majrp
					#print ciclo
					r=post("http://siiauescolar.siiau.udg.mx/wal/sfpcoal.horario",headers=self.__headers,data=params)
					out=r.text
					out=out[out.find("FECHA FIN"):]
					
					materias=[]
					
					cab='<TR bgcolor="#'
					cab2='<TR bgcolor="#FFFFFF">'
					cab3='<TR bgcolor="#e5e5e5">'
					cab4='<TD COLSPAN="5">'
					cab5='<TD>'
					while(cab2 in out or cab3 in out):
						out=out[out.find(cab):]
						out=out[out.find(">")+1:]
						if(out.find(cab4) != 1):
							out=out[out.find(cab5)+len(cab5):]
							nrc=out[:out.find("</TD>")]
							
							out=out[out.find(cab5)+len(cab5):]
							clave=out[:out.find("</TD>")]
							
							out=out[out.find(cab5)+len(cab5):]
							materia=out[:out.find("</TD>")]
							
							materias.append({"nrc":nrc,"clave":clave,"materia":materia})
							#print nrc,clave,materia
					self.carreras[cont]["materias_actuales"]=materias
				else:
					self.carreras[cont]["materias_actuales"]=[]
				cont=cont+1
		if(not encuesta):
			self.valido=True
						
			'''
			materias=[]
			cab='<TR bgcolor="'
			cab2="<FONT "
			print "Si entre aqui"
			print out
			while(cab in out):
				out=out[out.find(cab)+len(cab):]
				
				out=out[out.find(cab2)+len(cab2):]
				out=out[out.find(">")+1:]
				nrc=out[:out.find("</FONT>")]
				
				out=out[out.find(cab2)+len(cab2):]
				out=out[out.find(">")+1:]
				clave=out[:out.find("</FONT>")]
				
				out=out[out.find(cab2)+len(cab2):]
				out=out[out.find(">")+1:]
				materia=out[:out.find("</FONT>")]
				
				out=out[out.find(cab2)+len(cab2):]
				out=out[out.find(">")+1:]
				creditos=out[:out.find("</FONT>")]
				
				materias.append({"nrc":nrc,"clave":clave,"materia":materia,"creditos":creditos})
				print nrc,clave,materia,creditos
		self.carreras[cont]["materias_actuales"]=materias
		print self.carreras[cont]["materias_actuales"]
		cont=cont+1
		self.valido=True
		#print self.carreras[cont]
		#print "\n\n=====================================================\n\n"'''
	
	def __init__(self,codigo,nip):
		#print "Creando el objeto"
		self.codigo=""
		self.nip=""
		self.nombre=""
		self.items=[]
		self.carreras=[]
		valido=False
		#print "ehrkjerjkergjergjk"
		pidm=""
		self.codigo=codigo
		self.nip=nip
		#cmd="curl -c cookies.txt -i -A '"+self.__UA+"' -X POST -d 'p_codigo_c="+str(codigo)+"&p_clave_c="+str(nip)+"' siiauescolar.siiau.udg.mx/wus/gupprincipal.valida_inicio"
		params={"p_codigo_c":str(codigo),"p_clave_c":str(nip)}
		r=post("http://siiauescolar.siiau.udg.mx/wus/gupprincipal.valida_inicio",headers=self.__headers,data=params)
		out=r.text
		#out=getoutput(cmd)
		if('class="error"' not in out):
			#print "la clave y el nip son correctos"
			self.__COOKIES=r.cookies
			self.__getPidm(out)
			self.__getLink()
			#print self.carreras
			#getoutput("rm cookies.txt")
		else:
			self.valido=False
			#print "Los datos ingresados no son correctos"
			
class Profesor():
	
	__COOKIES=""
	
	__headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36',
	}
	
	pidm=""
	codigo=""
	nip=""
	nombre=""
	materias=[]
	
	valido=True
	
	def __getLink(self):
		#cmd="curl -L -b cookies.txt -i -A '"+self.__UA+"' -X GET siiauescolar.siiau.udg.mx/wus/gupmenug.menu_sistema?p_pidm_n="+str(self.pidm)
		r=get("http://siiauescolar.siiau.udg.mx/wus/gupmenug.menu_sistema?p_pidm_n="+str(self.pidm),headers=self.__headers,cookies=self.__COOKIES)
		out=r.text
		#out=getoutput(cmd)
		grado=""
		flag=True
		cab='<img src="/ows-img/closed.gif" alt="'
		cab2='<a href="'
		while(cab in out and flag):
			out=out[out.find(cab)+len(cab):]
			grado=out[:out.find('"')]
			out=out[out.find(cab2)+len(cab2):]
			link=out[:out.find('"')]
			#print link
			if(" " not in link):
				#print link
				flag=False
				self.__getCarreras(link)
		if(flag):
			self.items.append(None)
			self.__getInfoBasica();
	
	def __getPidm(self,text):
		cab='p_bienvenida_c" VALUE="'
		text=text[text.find(cab)+len(cab):]
		text=text[:text.find('"')]
		self.pidm=text
		#print text
		
	def __getInfoBasica(self):
		#print "aqui"
		r=get("http://siiauescolar.siiau.udg.mx/wpr/sipprac.lista_prof?pidmp="+self.pidm,headers=self.__headers,cookies=self.__COOKIES)
		out=r.text
		
		cab="<FONT "
		
		out=out[out.find("Nombre :"):]
		out=out[out.find(cab)+len(cab):]
		out=out[out.find(">")+1:]
		self.nombre=out[:out.find("</FONT>")]
		
		cab='<FONT COLOR="navy" FACE="arial" SIZE="2">'
		
		while(cab in out):
			out=out[out.find(cab)+len(cab):]
			ciclo=out[:out.find("</FONT>")]
			
			out=out[out.find(cab)+len(cab):]
			nrc=out[:out.find("</FONT>")]
			
			out=out[out.find(cab)+len(cab):]
			clave=out[:out.find("</FONT>")]
			
			out=out[out.find(cab)+len(cab):]
			nombre=out[:out.find("</FONT>")]
			
			self.materias.append({"ciclo":ciclo,"nrc":nrc,"clave":clave,"nombre":nombre})
		r=get("http://siiauescolar.siiau.udg.mx/wpr/silprac.asistencias_profesor",headers=self.__headers,cookies=self.__COOKIES)
		out=r.text
		cab='<TD style="font-family:arial;font-size:12;background-color:#ffffff;">'
		cab2='<A HREF='
		while(cab in out):
			out=out[out.find(cab)+len(cab):]
			ciclo=out[:out.find("</TD>")]
			
			out=out[out.find(cab)+len(cab):]
			nrc=out[:out.find("</TD>")]
			
			out=out[out.find(cab2)+len(cab2):]
			out=out[out.find(">")+1:]
			clave=out[:out.find("</A>")]
			
			out=out[out.find(cab)+len(cab):]
			nombre=out[:out.find("</TD>")]
			
			out=out[out.find("<TR>"):]
			
			self.materias.append({"ciclo":ciclo,"nrc":nrc,"clave":clave,"nombre":nombre})
			
		self.valido=True
		#print self.materias
		
	def __init__(self,codigo,nip):
		self.pidm=""
		self.nombre=""
		self.materias=[]
		#print "Creando el objeto"
		self.codigo=codigo
		self.nip=nip
		#cmd="curl -c cookies.txt -i -A '"+self.__UA+"' -X POST -d 'p_codigo_c="+str(codigo)+"&p_clave_c="+str(nip)+"' siiauescolar.siiau.udg.mx/wus/gupprincipal.valida_inicio"
		params={"p_codigo_c":str(codigo),"p_clave_c":str(nip)}
		r=post("http://siiauescolar.siiau.udg.mx/wus/gupprincipal.valida_inicio",headers=self.__headers,data=params)
		out=r.text
		#out=getoutput(cmd)
		if('class="error"' not in out):
			#print "la clave y el nip son correctos"
			self.__COOKIES=r.cookies
			self.__getPidm(out)
			self.__getInfoBasica()
			#print self.carreras
			#getoutput("rm cookies.txt")
		else:
			self.valido=False
			#print "Los datos ingresados no son correctos"
