#!/usr/bin/env node
/**
 * Aplicativo JavaScript de Exemplo para o Python App Launcher
 * Demonstra como o sistema detecta e executa aplicativos Node.js
 */

const os = require('os');
const path = require('path');

function main() {
    console.log("=".repeat(50));
    console.log("Python App Launcher - Aplicativo JavaScript de Exemplo");
    console.log("=".repeat(50));
    console.log(`Data e hora: ${new Date().toLocaleString('pt-BR')}`);
    console.log(`Node.js versão: ${process.version}`);
    console.log(`Sistema operacional: ${os.platform()} ${os.release()}`);
    console.log(`Arquitetura: ${os.arch()}`);
    console.log(`Executado a partir de: ${process.execPath}`);
    console.log("=".repeat(50));
    
    console.log("\nEste é um aplicativo JavaScript que demonstra:");
    console.log("✓ Detecção automática de linguagem JavaScript (Node.js)");
    console.log("✓ Execução segura pelo App Launcher");
    console.log("✓ Funcionamento correto do sistema Node.js");
    
    console.log("\nInformações do sistema:");
    console.log(`- CPUs: ${os.cpus().length}`);
    console.log(`- Memória total: ${Math.round(os.totalmem() / 1024 / 1024 / 1024)} GB`);
    console.log(`- Memória livre: ${Math.round(os.freemem() / 1024 / 1024 / 1024)} GB`);
    console.log(`- Diretório atual: ${process.cwd()}`);
    
    console.log("\n✅ Aplicativo JavaScript executado com sucesso!");
    console.log("O Python App Launcher está funcionando perfeitamente com Node.js!");
}

main(); 