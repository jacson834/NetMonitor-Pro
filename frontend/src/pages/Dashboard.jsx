import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

const Dashboard = () => {
  const [liveData, setLiveData] = useState({ upload: 0, download: 0 });
  const [alertLimit, setAlertLimit] = useState(5.0);
  const [chartPoints, setChartPoints] = useState(20);
  const [interfaceName, setInterfaceName] = useState('...');
  const [rawInterface, setRawInterface] = useState('all');
  const [availableInterfaces, setAvailableInterfaces] = useState([]);

  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      { label: 'Upload (MB/s)', data: [], borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.2)' },
      { label: 'Download (MB/s)', data: [], borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.2)' }
    ]
  });

  useEffect(() => {
    // Busca as interfaces de rede disponíveis ao carregar a página
    axios.get('http://localhost:8000/api/interfaces')
      .then(res => setAvailableInterfaces(res.data.interfaces))
      .catch(err => console.error("Erro ao buscar interfaces:", err));

    const ws = new WebSocket('ws://localhost:8000/api/ws');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const { upload, download } = data.stats;
      
      setLiveData({ upload, download });
      
      if (data.interface) {
        setRawInterface(data.interface); // Sincroniza o 'select' com o backend
        setInterfaceName(data.interface === 'all' ? 'Todas as Redes' : data.interface);
      }
      
      setChartData(prev => {
        // Mantém até 100 pontos na memória para permitir o ajuste visual
        const newLabels = [...prev.labels, new Date().toLocaleTimeString()].slice(-100);
        const newUp = [...prev.datasets[0].data, upload].slice(-100);
        const newDown = [...prev.datasets[1].data, download].slice(-100);
        
        return {
          labels: newLabels,
          datasets: [
            { ...prev.datasets[0], data: newUp },
            { ...prev.datasets[1], data: newDown }
          ]
        };
      });
    };

    return () => ws.close();
  }, []);

  const displayData = {
    labels: chartData.labels.slice(-chartPoints),
    datasets: chartData.datasets.map(ds => ({ ...ds, data: ds.data.slice(-chartPoints) }))
  };

  const handleInterfaceChange = (e) => {
    const newIface = e.target.value;
    axios.post('http://localhost:8000/api/interface', { interface: newIface }).catch(console.error);
  };

  const isUpAlert = liveData.upload > alertLimit;
  const isDownAlert = liveData.download > alertLimit;

  return (
    <div>
      <h1>
        Monitoramento em Tempo Real
        <span style={{ fontSize: '0.5em', color: '#888', marginLeft: '10px', fontWeight: 'normal' }}>
          ({interfaceName})
        </span>
      </h1>
      
      <div className="settings-panel" style={{ background: '#1e1e1e', padding: '15px', borderRadius: '8px', marginBottom: '20px', display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
        <div>
          <label style={{ marginRight: '10px' }}>Rede: </label>
          <select value={rawInterface} onChange={handleInterfaceChange} style={{ background: '#333', color: '#fff', border: '1px solid #444', padding: '5px', borderRadius: '4px' }}>
            {availableInterfaces.map(iface => (
              <option key={iface} value={iface}>
                {iface === 'all' ? 'Todas as Redes' : iface}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label style={{ marginRight: '10px' }}>Alerta Visual (MB/s): </label>
          <input type="number" value={alertLimit} onChange={(e) => setAlertLimit(Number(e.target.value))} style={{ width: '80px', background: '#333', color: '#fff', border: '1px solid #444', padding: '5px', borderRadius: '4px' }} />
        </div>
        <div>
          <label style={{ marginRight: '10px' }}>Pontos no Gráfico: </label>
          <input type="number" value={chartPoints} onChange={(e) => setChartPoints(Number(e.target.value))} style={{ width: '80px', background: '#333', color: '#fff', border: '1px solid #444', padding: '5px', borderRadius: '4px' }} />
        </div>
      </div>

      <div className="cards">
        <div className="card" style={{ border: isUpAlert ? '2px solid #ef4444' : '2px solid transparent' }}>
          <h3>⬆ Upload</h3>
          <p className="val" style={{ color: isUpAlert ? '#ef4444' : '#00ff00' }}>{liveData.upload.toFixed(2)} MB/s</p>
        </div>
        <div className="card" style={{ border: isDownAlert ? '2px solid #ef4444' : '2px solid transparent' }}>
          <h3>⬇ Download</h3>
          <p className="val" style={{ color: isDownAlert ? '#ef4444' : '#00ff00' }}>{liveData.download.toFixed(2)} MB/s</p>
        </div>
      </div>
      <div className="chart-container" style={{height: '400px', marginTop: '20px'}}>
        <Line 
          data={displayData} 
          options={{ responsive: true, maintainAspectRatio: false, animation: { duration: 0 } }} 
        />
      </div>
    </div>
  );
};

export default Dashboard;