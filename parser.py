# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 01:33:31 2022

@author: Asterisk
"""
import xml.etree.ElementTree as ET
from pathlib import Path

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
duplicates = set()
for file in chunk.rglob("*.xml"):
    if file.stem in knownPairs:
        text = pairedTextFiles(str(file),
                               str(file).replace(file.stem,
                                                 knownPairs[file.stem]))
    elif file.stem in pairTargets:
        continue
    else:
        text = singleTextFiles(str(file))
    master.append("\n\n## %s\n"%file.stem)
    for key,(title,description) in text.items():
        if description in duplicates:
            continue
        duplicates.add(description)
        if title:
            master.append("\n### %s [%d]"%(title,key))
            master.append(description)
        else:
            master.append("[%d] %s"%(key,description))
with open("Master.md","w",encoding = "utf8") as outf:
    outf.write("\n".join(master))