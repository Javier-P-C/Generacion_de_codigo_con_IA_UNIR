import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { salesAPI } from '../api';

const Sales = () => {
  const navigate = useNavigate();
  const { data: sales = [], isLoading } = useQuery({
    queryKey: ['sales'],
    queryFn: salesAPI.list,
  });

  if (isLoading) return <div>Loading sales...</div>;

  return (
    <div>
      <h1>Sales History</h1>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          marginTop: '1rem',
        }}
      >
        <thead>
          <tr style={{ background: '#34495e', color: 'white' }}>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>ID</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Employee</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Date</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Total</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sales.map((sale) => (
            <tr key={sale.id} style={{ borderBottom: '1px solid #ddd' }}>
              <td style={{ padding: '0.75rem' }}>{sale.id}</td>
              <td style={{ padding: '0.75rem' }}>{sale.employee_name}</td>
              <td style={{ padding: '0.75rem' }}>{new Date(sale.date).toLocaleString()}</td>
              <td style={{ padding: '0.75rem' }}>${sale.total}</td>
              <td style={{ padding: '0.75rem' }}>
                <button
                  onClick={() => navigate(`/sales/${sale.id}`)}
                  style={{
                    background: '#3498db',
                    color: 'white',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    cursor: 'pointer',
                    borderRadius: '4px',
                  }}
                >
                  View Details
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Sales;
