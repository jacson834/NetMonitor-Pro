import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

const History = () => {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/history')
      .then(res => {
        const data = res.data;
        setChartData({
          labels: data.map(d => new Date(d.timestamp).toLocaleTimeString()),
          datasets: [
            { label: 'Upload Histórico', data: data.map(d => d.upload_mbps), borderColor: '#ef4444' },
            { label: 'Download Histórico', data: data.map(d => d.download_mbps), borderColor: '#3b82f6' }
          ]
        });
      });
  }, []);

  return (
    <div>
      <h1>Histórico Recente</h1>
      {chartData ? (
        <div className="chart-container" style={{height: '400px'}}>
          <Line data={chartData} options={{ responsive: true, maintainAspectRatio: false }} />
        </div>
      ) : (
        <p>Carregando...</p>
      )}
    </div>
  );
};

export default History;