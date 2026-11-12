#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';

const source=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!fs.existsSync(path.join(source,'SKILL.md')))throw new Error('Incomplete package: SKILL.md is missing.');
const args=process.argv.slice(2);
if(args.includes('--help')){
 console.log('Usage: node scripts/install.mjs [--dest SKILLS_DIRECTORY] [--replace]\nDefault: $CODEX_HOME/skills or ~/.codex/skills. Existing installations are never overwritten without --replace.');
 process.exit(0);
}
let destRoot=path.join(process.env.CODEX_HOME||path.join(os.homedir(),'.codex'),'skills');
let replace=false;
for(let i=0;i<args.length;i++){
 if(args[i]==='--dest'&&args[i+1])destRoot=path.resolve(args[++i]);
 else if(args[i]==='--replace')replace=true;
 else throw new Error('Unknown or incomplete argument: '+args[i]);
}
const destination=path.join(destRoot,'yu-apple');
if(destination===source)throw new Error('Source and destination are identical; choose another skills directory.');
const blocked=new Set(['.git','node_modules','out','output','.tmp','.DS_Store']);
const copyFilter=(item)=>{
 const rel=path.relative(source,item);
 if(!rel)return true;
 const parts=rel.split(path.sep);
 return !parts.some(p=>blocked.has(p)||p==='.env'||p.startsWith('.env.'));
};
let backup;
if(fs.existsSync(destination)){
 if(!replace)throw new Error('Installation already exists. Use --replace to back it up and install this version.');
 const stamp=new Date().toISOString().replaceAll(':','-').replaceAll('.','-');
 const backups=path.join(path.dirname(destRoot),'skill-backups');
 fs.mkdirSync(backups,{recursive:true});
 backup=path.join(backups,'yu-apple-'+stamp);
 fs.renameSync(destination,backup);
}
fs.mkdirSync(destRoot,{recursive:true});
try {fs.cpSync(source,destination,{recursive:true,filter:copyFilter,errorOnExist:true,force:false});}
catch(error){
 if(fs.existsSync(destination))fs.rmSync(destination,{recursive:true,force:true});
 if(backup)fs.renameSync(backup,destination);
 throw error;
}
console.log(JSON.stringify({installed:destination,backup:backup||null,next:'Open a new turn and invoke $yu-apple. For rendering, install the package dependencies and Chromium in this folder.'},null,2));
