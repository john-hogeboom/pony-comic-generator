from PIL import Image,ImageFont,ImageDraw
import random
from pprint import pprint
import generatePanel
import findEmote
import textwrap
import os
import pyperclip
import StringIO
import ConfigParser, os
from imgurpython import ImgurClient
import praw
import sys
import urllib
import os


#direct print output to log file
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("log.txt", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

sys.stdout = Logger()


imgareio = '174becf08a64efc'
imgscrioertu = 'c47422a4a3a7a4aab366b88634bcc03a0ffcaa60'
client = ImgurClient(imgareio, imgscrioertu)

try:
	urllib.urlretrieve('https://raw.githubusercontent.com/chickens2/pony-comic-generator/master/DEFAULT_ALIAS_DO_NOT_EDIT.cfg','DEFAULT_ALIAS_DO_NOT_EDIT.cfg')
except:
	print 'could not retrieve default alias list, using local version'
config2 = ConfigParser.ConfigParser()
config2.readfp(open('DEFAULT_ALIAS_DO_NOT_EDIT.cfg'))
allNames=dict(config2.items('Aliases'))

config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

allText=""
lines=[]
allNames.update(dict(config.items('Aliases'))) #add aliases from config.cfg, overwrite defaults
names={}
selectedBackground=None
fntLarge = ImageFont.truetype('fonts/cpsb.ttf', 25)
fntMed= ImageFont.truetype('fonts/cpsb.ttf', 17)
fntSmall= ImageFont.truetype('fonts/cpsb.ttf', 12)
anonymousMode=config.get('Options','anonymous_mode')=='True'
uploadImgur=config.get('Options','upload_imgur')=='True'

uploadReddit=None
reddit = None
if config.has_section('praw') and len(config.get('praw','clientid'))>2:
	#print 'praw stuff:'+config.get('praw','clientid')+"^"
	uploadReddit=config.get('praw','upload')
	reddit = praw.Reddit(client_id=config.get('praw','clientid'),
					client_secret=config.get('praw','clientsecret'),
					user_agent='user agent',
					username=config.get('praw','username'),
					password=config.get('praw','password'))
	print 'reddit credentials:'+str(config.get('praw','clientsecret'))+" "+config.get('praw','clientid')
#sys.exit()
def anonymizeText(text):
	newtext=text
	newWords=[]
	if anonymousMode:
		words=text.split(" ")
		#print 'anonymizing'
		for word in words:
			if len(word)>=4:
				#print 'considering word '+word
				for name in allNames.keys():
					#print 'comparing to '+name
					if word.lower() in name.lower():
						word=names[name]
						break
			newWords.append(word)
		newtext=" ".join(newWords)
	return newtext
def findBetween(s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
def drawCenteredText(startY,text,draw,fnt,panelSize):
	
	MAX_W, MAX_H = panelSize[0], panelSize[1]
	para=textwrap.wrap(text, width=12)
	print 'para:'
	pprint(para)
	current_h, pad = startY, 10
	#draw.text((5,5),para[0],font=fnt)
	for line in para:
		w, h = draw.textsize(line, font=fnt)
		draw.text(((MAX_W - w) / 2, current_h), line, font=fnt,fill=(0,0,0,255))
		current_h += h + pad
	return current_h
def getTitle():
	random.seed(allText)
	#pprint(names)
	line=random.choice(lines)
	words=line['text'].split(" ")
	if len(words)>5:
		words=words[-5:]
	title=None
	while len(words)>2 and random.random()>0.4:
		print words[0]
		del words[0]
		#print 'words:'
		#pprint(words)
	title=" ".join(words).title()
	#title=textwrap.wrap(title, width=15)
	print 'title '+str(title)
	return title
def createTitlePanel(panelSize):
	title=getTitle()
	img = Image.new("RGBA", panelSize, (255,255,255))
	d = ImageDraw.Draw(img)
	newh=drawCenteredText(25,title,d,fntLarge,panelSize)
	newh+=17
	d.text((15,newh), "With:", font=fntSmall, fill=(0,0,0,255))
	newh+=15
	for key,value in names.iteritems():
		text=value
		if not anonymousMode:
			text=text+" as "+key
		d.text((15,newh), text, font=fntSmall, fill=(0,0,0,255))
		newh+=15
	generatePanel.drawBorder(img)
	return img#img.show()
def isCorrectOrder(txtLine1,txtLine2,nameorder):
	print 'comparing nameorder '+str(nameorder)+" "+txtLine2['name']
	for name in nameorder:
		if name == txtLine2['name']:
			return False
		if name == txtLine1['name']:
			return True
	return True
prevNames=[]
def createNextPanel(txtLines,panelSize,smallPanels,nameorder,closeup=True):
	global prevNames
	dialogueOptions=[0]
	generatePanel.setPanelSize(panelSize)
	print 'nameorder: '+str(nameorder)
	print 'gppanelsize '+str(generatePanel.panelSize)+" "+str(panelSize)
	if len(txtLines)>1 and txtLines[1]['name'] != txtLines[0]['name'] and generatePanel.hasRoomForDialogue2(txtLines[0]['text'],txtLines[1]['text'] ):
		dialogueOptions.append(1)
		if len(txtLines)>2 and txtLines[2]['name'] != txtLines[1]['name'] and txtLines[0]['name'] != txtLines[2]['name'] and generatePanel.hasRoomForDialogue3(txtLines[0]['text'],txtLines[1]['text'],txtLines[2]['text'] ):
			dialogueOptions.append(2)
	random.seed(str(txtLines))
	dialogueChoice=random.choice(dialogueOptions)
	panel=None
	
	currentNames=[]
	print 'prevnames to start '+str(dialogueChoice)+" "+str(range(dialogueChoice))
	pprint(prevNames)
	for i in range(dialogueChoice+1):
		name=txtLines[i]['name']
		print 'should be removing name '+name
		if name in prevNames: prevNames.remove(name)
		currentNames.append(name)
	print 'prevnames after'
	pprint(prevNames)
	for name in prevNames:
		if dialogueChoice>=2:
			break
		else:
			dialogueChoice+=1
			txtLines.insert(0,{'name':name,'text':''})
			#currentNames.append(name)
	print 'txtLines: '
	pprint(txtLines)
	if dialogueChoice==0:
		panel=generatePanel.drawPanel1Character(txtLines[0]['name'],txtLines[0]['text'],selectedBackground,iscloseup=closeup)
		del txtLines[0]
	if dialogueChoice==1:
		print 'iscorrectorder: '+str(isCorrectOrder(txtLines[0],txtLines[1],nameorder))
		if isCorrectOrder(txtLines[0],txtLines[1],nameorder):
			panel=generatePanel.drawPanel2Characters(txtLines[0]['name'],txtLines[1]['name'],txtLines[0]['text'],txtLines[1]['text'],selectedBackground,iscloseup=closeup)
		else:
			panel=generatePanel.drawPanel2Characters(txtLines[1]['name'],txtLines[0]['name'],txtLines[0]['text'],txtLines[1]['text'],selectedBackground,textOrder=1,iscloseup=closeup)
		del txtLines[0]
		del txtLines[0]
	if dialogueChoice==2:
		panel=generatePanel.drawPanel3Characters(txtLines[0]['name'],txtLines[1]['name'],txtLines[2]['name'],txtLines[0]['text'],txtLines[1]['text'],txtLines[2]['text'],selectedBackground,iscloseup=closeup)
		del txtLines[0]
		del txtLines[0]
		del txtLines[0]
	prevNames=currentNames
	print 'returning panel '+str(panel)+" "+str(dialogueChoice)
	return panel
def selectBackground(seed):
	random.seed(seed)
	return 'backgrounds/'+random.choice(os.listdir('backgrounds'))
def processChatLog(file):
	global selectedBackground
	global lines
	global allNames
	print 'original allnames:'
	pprint(allNames)
	text=""
	mostInARow=1
	currentName=None
	currentInARow=1
	nameOrder=[]
	for line in file:
		#if 'Raribot' in line or '> ~' in line:
		#	continue
		line=line.strip()
		line=line.strip('\n')
		text+=line
		print 'line:'+line
		if line[:2]=="* " and '(Quit:' not in line and ' has joined' not in line:
			line=line[2:]
			line='<'+line[:line.index(' ')]+'> *'+line[line.index(' ')+1:]+'*'
			print 'new line '+line
		if line.count('<')<1 or line.count('>')<1:
			continue
		name=findBetween(line,'<','>').lower()
		if name not in nameOrder:
			nameOrder.append(name)
		pony=None
		if name not in allNames:
			print 'name '+str(name)+' not in allnames'
			pony=findEmote.getProceduralPony(name)
			names[name]=pony
			allNames[name]=pony
		else:
			print 'name '+str(name)+' was in allnames'
			names[name]=allNames[name]
			pony=names[name]
		print 'name: '+name
		line=line[line.index('>')+2:]
		lines.append({"pony":pony,"name":name,"text":line})
		
		
		if name==currentName:
			currentInARow+=1
			if currentInARow>mostInARow:
				mostInARow=currentInARow
		else:
			currentInARow=1
		currentName=name
	#this is a bad hack probably but idk how else to do it without adding a million extra parameters everywhere
	print 'the final names list: '
	pprint(names)
	generatePanel.names=names
	print 'most in a row: '+str(mostInARow)
	for line in lines:
		if anonymousMode:
			line['text']=anonymizeText(line['text'])
	#print 'lines:'
	#pprint(lines)
	#return
	selectedBackground=selectBackground(text)
	#pprint(names)
	global allText
	allText=text
	#print 'at1'+str(allText)+'^'
	smallPanels=False
	panelSize=(300,300)
	if mostInARow>3:
		smallPanels=True
		panelSize=(200,200)
	tp=createTitlePanel(panelSize)
	print 'generatecomic panelsize: '+str(panelSize)
	#tp.show()
	panels=[]
	panels.append(tp)
	txtLines=list(lines)
	while len(txtLines)>0:
		panels.append(createNextPanel(txtLines,panelSize,smallPanels,nameOrder))
	panelsAcross=2
	if smallPanels:
		panelsAcross=3
	#if it needs an establishing shot with no dialogue
	if len(panels)%panelsAcross!=0:
		panels.insert(1,generatePanel.drawPanelNoDialogue(nameOrder[:min(3,len(nameOrder))],selectedBackground,text+str(len(panels))))
	else: #otherwise redo the first panel as zoomed out
		txtLines2=list(lines)
		del panels[1]
		panels.insert(1,createNextPanel(txtLines2,panelSize,smallPanels,nameOrder,closeup=False))
	#if there still aren't enough panels, pad the end
	while len(panels)%panelsAcross!=0:
		panels.append(generatePanel.drawPanelNoDialogue(prevNames,selectedBackground,text+str(len(panels))))
	maxWidth=panelSize[0]*panelsAcross
	currentHeight=0
	currentWidth=0
	img=Image.new('RGBA',(maxWidth,panelSize[1]*len(panels)/panelsAcross))
	print 'comic dimensions: '+str(img.size)
	print 'small panels: '+str(smallPanels)
	print 'panels:'
	pprint(panels)
	for panel in panels:
		box=(currentWidth,currentHeight,currentWidth+panel.size[0],panel.size[1]+currentHeight)
		print 'making panel at: '+str(box)
		img.paste(panel,box)
		currentWidth+=panel.size[0]
		if currentWidth>=maxWidth:
			currentWidth=0
			currentHeight+=panel.size[1]
	#img.show()
	img.save("comic.jpg","JPEG")

	

clipboard=pyperclip.paste().encode('utf8')
print 'clipboard is: \n'+str(clipboard)
processChatLog(StringIO.StringIO(clipboard))#open('exampleChat12.txt','r'))
if uploadImgur:
	image=client.upload_from_path('comic.jpg')
	pyperclip.copy(image['link'])
	print image['link']
	if uploadReddit:
		thetitle=getTitle()
		print 'title '+thetitle+" link "+image['link']
		reddit.subreddit("beniscity").submit(title=thetitle,url=image['link'])