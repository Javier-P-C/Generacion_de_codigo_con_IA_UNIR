import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { salesAPI } from '../api';

const SaleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: sale, isLoading: loadingSale } = useQuery({
    queryKey: ['sale', id],
    queryFn: () => salesAPI.get(id),
  });

  const { data: details = [], isLoading: loadingDetails } = useQuery({
    queryKey: ['saleDetails', id],
    queryFn: () => salesAPI.getDetails(id),
  });

  if (loadingSale || loadingDetails) return <div>Loading sale details...</div>;

  return (
    <div>
      <button
        onClick={() => navigate('/sales')}
        style={{
          background: '#95a5a6',
          color: 'white',
          border: 'none',
          padding: '0.5rem 1rem',
          cursor: 'pointer',
          borderRadius: '4px',
          marginBottom: '1rem',
        }}
      >
        ← Back to Sales
      </button>

      <h1>Sale #{sale?.id}</h1>
      <div
        style={{
          padding: '1rem',
          background: '#ecf0f1',
          borderRadius: '4px',
          marginBottom: '1rem',
        }}
      >
        <p>
          <strong>Employee:</strong> {sale?.employee_name}
        </p>
        <p>
          <strong>Date:</strong> {sale ? new Date(sale.date).toLocaleString() : ''}
        </p>
        <p>
          <strong>Total:</strong> ${sale?.total}
        </p>
      </div>

      <h2>Sale Items</h2>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          marginTop: '1rem',
        }}
      >
        <thead>
          <tr style={{ background: '#34495e', color: 'white' }}>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Product</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Presentation</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Quantity</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Unit Price</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {details.map((detail) => (
            <tr key={detail.id} style={{ borderBottom: '1px solid #ddd' }}>
              <td style={{ padding: '0.75rem' }}>{detail.product.name}</td>
              <td style={{ padding: '0.75rem' }}>{detail.product.presentation}</td>
              <td style={{ padding: '0.75rem' }}>{detail.quantity}</td>
              <td style={{ padding: '0.75rem' }}>${detail.product.price}</td>
              <td style={{ padding: '0.75rem' }}>${detail.subtotal}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SaleDetail;
