# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 01:33:31 2022

@author: Asterisk
"""
import xml.etree.ElementTree as ET
import markdown

from pathlib import Path

npcOverloads = {}

def loadNPCNames():
    path = r".\item\GR\data\INTERROOT_win64\msg\engUS\NpcName.fmg.xml"
    npcNames = loadTextFile(path)
    remapping = {}
    for ids in npcNames:
        if str(ids)[0] == "1":
            remapping[int(str(ids)[1:-1])] = npcNames[ids]
    for key in npcOverloads:
        remapping[key] = npcOverloads[key]
    return remapping

def parseNPCDialogue(path, npcNames = {},output = print):
    l_npc = 0
    l_section = 0
    data = loadTextFile(path)
    for identifier in data:
        step = identifier%1000
        section = (identifier//1000)%100
        npc = (identifier//100000)
        if npc != l_npc:
            if npc in npcNames:
                output("### %s [%04d]"%(npcNames[npc],npc))
            else:
                output("### %04d"%(npc))
            l_npc = npc
            l_section = -1
        if section != l_section:
            output("#### Section %02d"%section)
            l_section = section
        if data[identifier]:
            output("[%d] "%(identifier) + data[identifier]+"  ")
    return

def loadTextFile(path):
    tree = ET.parse(path)
    root = tree.getroot()
    textElements = root.getchildren()[3].getchildren()
    elements = {}
    for element in textElements:
        identifier = int(element.items()[0][1])
        text = element.text
        if "%null%" not in text:
            elements[identifier] = text
    return elements

def pairedTextFiles(path0,path1):
    merged = {}
    l,r = map(loadTextFile,[path0,path1])
    for key in l:
        if key in r:
            merged[key] = (l[key],r[key])
        else:
            merged[key] = (l[key],"")
    for key in r:
        if key not in merged:
            merged[key] = ("",r[key])
    return merged

def singleTextFiles(path):
    l = loadTextFile(path)
    m = {}
    for key in l:
        m[key] = ("",l[key])
    return m

chunk = Path(r".")
knownPairs = {"TutorialTitle":"TutorialBody",
              "LoadingTitle":"LoadingText",
              "AccessoryName":"AccessoryCaption",
              "ArtsName":"ArtsCaption",
              "GemName":"GemCaption",
              "GoodsName":"GoodsCaption",
              "MagicName":"MagicCaption",
              "ProtectorName":"ProtectorCaption",
              "WeaponName":"WeaponCaption",
              }
knownPairs = {k+".fmg":t+".fmg" for k,t in knownPairs.items()}
pairTargets = {knownPairs[p]:p for p in knownPairs}
master = []
npcIds = loadNPCNames()
duplicates = set()
for file in chunk.rglob("*.xml"):
    if "ToS" in file.stem:
        continue
    if file.stem in knownPairs:
        text = pairedTextFiles(str(file),
                               str(file).replace(file.stem,
                                                 knownPairs[file.stem]))
    elif file.stem in pairTargets:
        continue
    else:
        text = singleTextFiles(str(file))
    master.append("\n\n## %s\n"%file.stem)
    if file.stem == "TalkMsg.fmg":
        parseNPCDialogue(file,npcIds,master.append)
    else:
        for key,(title,description) in text.items():
            if description in duplicates:
                continue
            duplicates.add(description)
            if title:
                master.append("\n### %s [%d]"%(title,key))
                master.append(description)
            else:
                master.append("[%d] %s\n"%(key,description))
text = "\n".join(master)
with open("Master.html","w",encoding = "utf8") as outf:
    outf.write(markdown.markdown(text))
    
