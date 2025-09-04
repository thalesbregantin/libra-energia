import { NextResponse } from 'next/server'
import { readFileSync } from 'fs'
import { join } from 'path'

export async function GET() {
  try {
    // Tenta ler o arquivo mais recente de leads
    const dataPath = join(process.cwd(), '..', 'src', 'leads_coletados_20250903_171709.json')
    
    try {
      const fileContent = readFileSync(dataPath, 'utf-8')
      const leads = JSON.parse(fileContent)
      
      return NextResponse.json(leads, {
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache'
        }
      })
    } catch (fileError) {
      // Se não conseguir ler o arquivo, retorna erro 404
      return NextResponse.json(
        { error: 'Arquivo de leads não encontrado' },
        { status: 404 }
      )
    }
  } catch (error) {
    console.error('Erro na API de leads:', error)
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    )
  }
}
