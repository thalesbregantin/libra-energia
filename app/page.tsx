'use client'

import { useState, useEffect } from 'react'
import { 
  Zap, 
  Users, 
  TrendingUp, 
  Target, 
  Filter,
  Download,
  RefreshCw,
  BarChart3,
  PieChart,
  Activity,
  Database,
  AlertCircle
} from 'lucide-react'
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line } from 'recharts'

interface Lead {
  id?: string
  nome: string
  telefone: string
  website: string
  endereco: string
  cnae?: string
  score: number
  qualificado: boolean
  nivel_qualificacao: 'Alto' | 'Médio' | 'Baixo'
  criterios_atingidos: string[]
  fonte: string
  data_coleta: string
  categoria?: string[]
  nota?: number
  reviews?: number
  latitude?: number
  longitude?: number
  place_id?: string
  horario_funcionamento?: string[]
  nivel_preco?: number
}

export default function Dashboard() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [filteredLeads, setFilteredLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [dataStatus, setDataStatus] = useState<'loading' | 'success' | 'error' | 'warning'>('loading')
  const [dataMessage, setDataMessage] = useState('Carregando dados...')
  const [lastUpdate, setLastUpdate] = useState<string>('')
  const [filters, setFilters] = useState({
    nivel: 'Todos',
    scoreMin: 0,
    fonte: 'Todas',
    nome: ''
  })

  // Dados de exemplo para fallback
  const sampleLeads: Lead[] = [
    {
      id: '1',
      nome: 'Supermercado Exemplo Ltda',
      telefone: '(11) 99999-9999',
      website: 'https://www.exemplo.com.br',
      endereco: 'Rua das Flores, 123, Centro, São Paulo, SP',
      cnae: '4721-1/01',
      score: 5,
      qualificado: true,
      nivel_qualificacao: 'Alto',
      criterios_atingidos: ['Telefone válido', 'CNAE compatível', 'Endereço válido', 'Nome válido'],
      fonte: 'Google Places',
      data_coleta: '03/09/2025 16:30:00'
    },
    {
      id: '2',
      nome: 'Padaria do João',
      telefone: '(11) 88888-8888',
      website: '',
      endereco: 'Av. Paulista, 456, Bela Vista, São Paulo, SP',
      cnae: '4722-0/00',
      score: 5,
      qualificado: true,
      nivel_qualificacao: 'Alto',
      criterios_atingidos: ['Telefone válido', 'CNAE compatível', 'Endereço válido', 'Nome válido'],
      fonte: 'Google Places',
      data_coleta: '03/09/2025 16:30:00'
    },
    {
      id: '3',
      nome: 'Academia Fitness',
      telefone: '(11) 77777-7777',
      website: 'https://academiafitness.com.br',
      endereco: 'Rua Augusta, 789, Consolação, São Paulo, SP',
      cnae: '9311-5/01',
      score: 6,
      qualificado: true,
      nivel_qualificacao: 'Alto',
      criterios_atingidos: ['Telefone válido', 'CNAE compatível', 'Mídia social', 'Endereço válido', 'Nome válido'],
      fonte: 'Instagram',
      data_coleta: '03/09/2025 16:30:00'
    }
  ]

  // Função para carregar dados reais
  const loadRealData = async () => {
    try {
      setDataStatus('loading')
      setDataMessage('Carregando dados reais...')
      
      // Tenta carregar o arquivo mais recente de leads
      const response = await fetch('/api/leads')
      if (response.ok) {
        const data = await response.json()
        setLeads(data)
        setFilteredLeads(data)
        setDataStatus('success')
        setDataMessage(`Dados carregados: ${data.length} leads`)
        setLastUpdate(new Date().toLocaleString('pt-BR'))
      } else {
        // Se não conseguir carregar via API, tenta carregar arquivo local
        const localResponse = await fetch('/leads_coletados_20250903_171709.json')
        if (localResponse.ok) {
          const data = await localResponse.json()
          setLeads(data)
          setFilteredLeads(data)
          setDataStatus('success')
          setDataMessage(`Dados carregados: ${data.length} leads`)
          setLastUpdate(new Date().toLocaleString('pt-BR'))
        } else {
          // Fallback para dados de exemplo
          setLeads(sampleLeads)
          setFilteredLeads(sampleLeads)
          setDataStatus('warning')
          setDataMessage('Usando dados de exemplo (arquivo não encontrado)')
        }
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error)
      setLeads(sampleLeads)
      setFilteredLeads(sampleLeads)
      setDataStatus('error')
      setDataMessage('Erro ao carregar dados. Usando dados de exemplo.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRealData()
  }, [])

  useEffect(() => {
    // Aplica filtros
    let filtered = leads

    if (filters.nivel !== 'Todos') {
      filtered = filtered.filter(lead => lead.nivel_qualificacao === filters.nivel)
    }

    if (filters.scoreMin > 0) {
      filtered = filtered.filter(lead => (lead.score || 0) >= filters.scoreMin)
    }

    if (filters.fonte !== 'Todas') {
      filtered = filtered.filter(lead => lead.fonte === filters.fonte)
    }

    if (filters.nome) {
      filtered = filtered.filter(lead => 
        lead.nome.toLowerCase().includes(filters.nome.toLowerCase())
      )
    }

    setFilteredLeads(filtered)
  }, [leads, filters])

  const handleFilterChange = (key: string, value: string | number) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const exportToCSV = () => {
    const headers = ['Nome', 'Telefone', 'Website', 'Endereço', 'Score', 'Nível', 'Qualificado', 'Fonte', 'Data']
    const csvContent = [
      headers.join(','),
      ...filteredLeads.map(lead => [
        lead.nome || 'N/A',
        lead.telefone || 'N/A',
        lead.website || '',
        lead.endereco || 'N/A',
        lead.score || 0,
        lead.nivel_qualificacao || 'Baixo',
        lead.qualificado ? 'Sim' : 'Não',
        lead.fonte || 'N/A',
        lead.data_coleta || 'N/A'
      ].join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `leads_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-400'
      case 'warning': return 'bg-yellow-400'
      case 'error': return 'bg-red-400'
      case 'loading': return 'bg-blue-400'
      default: return 'bg-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <Database className="w-4 h-4" />
      case 'warning': return <AlertCircle className="w-4 h-4" />
      case 'error': return <AlertCircle className="w-4 h-4" />
      case 'loading': return <RefreshCw className="w-4 h-4 animate-spin" />
      default: return <Database className="w-4 h-4" />
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700">Carregando dashboard...</h2>
        </div>
      </div>
    )
  }

  const stats = {
    total: leads.length,
    qualificados: leads.filter(l => l.qualificado).length,
    scoreMedio: leads.length > 0 ? (leads.reduce((sum, l) => sum + (l.score || 0), 0) / leads.length).toFixed(1) : '0',
    taxaQualificacao: leads.length > 0 ? ((leads.filter(l => l.qualificado).length / leads.length) * 100).toFixed(1) : '0'
  }

  const nivelData = [
    { name: 'Alto', value: leads.filter(l => l.nivel_qualificacao === 'Alto').length, color: '#10b981' },
    { name: 'Médio', value: leads.filter(l => l.nivel_qualificacao === 'Médio').length, color: '#f59e0b' },
    { name: 'Baixo', value: leads.filter(l => l.nivel_qualificacao === 'Baixo').length, color: '#ef4444' }
  ]

  const scoreData = leads.slice(0, 10).map(lead => ({ 
    name: lead.nome || 'N/A', 
    score: lead.score || 0 
  }))

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-lg mr-3 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">
                Libra Energia - Dashboard de Prospecção
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={loadRealData}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Atualizar
              </button>
              <button 
                onClick={exportToCSV}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <Download className="w-4 h-4 mr-2" />
                Exportar CSV
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status dos Dados */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className={`w-3 h-3 ${getStatusColor(dataStatus)} rounded-full mr-2`}></div>
              <span className="text-sm text-gray-600">{dataMessage}</span>
            </div>
            <div className="text-sm text-gray-500">{lastUpdate}</div>
          </div>
        </div>

        {/* Métricas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total de Leads</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Target className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Leads Qualificados</p>
                <p className="text-2xl font-bold text-gray-900">{stats.qualificados}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <BarChart3 className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Score Médio</p>
                <p className="text-2xl font-bold text-gray-900">{stats.scoreMedio}/6</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Taxa de Qualificação</p>
                <p className="text-2xl font-bold text-gray-900">{stats.taxaQualificacao}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Distribuição por Nível</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RechartsPieChart>
                <Pie
                  data={nivelData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {nivelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Score por Lead (Top 10)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={scoreData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis domain={[0, 6]} />
                <Tooltip />
                <Bar dataKey="score" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Filtros */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Filtros e Busca</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nível de Qualificação
              </label>
              <select 
                value={filters.nivel}
                onChange={(e) => handleFilterChange('nivel', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Todos">Todos</option>
                <option value="Alto">Alto</option>
                <option value="Médio">Médio</option>
                <option value="Baixo">Baixo</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Score Mínimo
              </label>
              <input 
                type="range" 
                min="0" 
                max="6" 
                value={filters.scoreMin}
                onChange={(e) => handleFilterChange('scoreMin', parseInt(e.target.value))}
                className="w-full"
              />
              <div className="text-sm text-gray-500 mt-1">{filters.scoreMin}/6</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fonte
              </label>
              <select 
                value={filters.fonte}
                onChange={(e) => handleFilterChange('fonte', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Todas">Todas</option>
                <option value="Google Places">Google Places</option>
                <option value="Instagram">Instagram</option>
                <option value="Receita Federal">Receita Federal</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Buscar por Nome
              </label>
              <input 
                type="text" 
                placeholder="Digite o nome..." 
                value={filters.nome}
                onChange={(e) => handleFilterChange('nome', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Tabela de Leads */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">
                Lista de Leads ({filteredLeads.length} encontrados)
              </h3>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Telefone</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Website</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nível</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fonte</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredLeads.map((lead, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{lead.nome || 'N/A'}</div>
                      <div className="text-sm text-gray-500">{lead.endereco || 'Endereço não informado'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{lead.telefone || 'N/A'}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {lead.website ? (
                        <a 
                          href={lead.website} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-900 text-sm"
                        >
                          Visitar
                        </a>
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        (lead.score || 0) >= 5 ? 'bg-green-100 text-green-800' :
                        (lead.score || 0) >= 3 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {lead.score || 0}/6
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        (lead.nivel_qualificacao || 'Baixo') === 'Alto' ? 'bg-green-100 text-green-800' :
                        (lead.nivel_qualificacao || 'Baixo') === 'Médio' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {lead.nivel_qualificacao || 'Baixo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{lead.fonte || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
