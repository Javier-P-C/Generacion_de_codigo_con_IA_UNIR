import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventoryAPI } from '../api';
import useAuthStore from '../stores/authStore';

const Inventory = () => {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState(null);
  const [amount, setAmount] = useState(1);
  const [error, setError] = useState('');

  const { data: inventory = [], isLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: inventoryAPI.list,
  });

  const increaseMutation = useMutation({
    mutationFn: ({ id, amount }) => inventoryAPI.increase(id, amount),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      setSelectedId(null);
      setAmount(1);
      setError('');
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Failed to increase inventory');
    },
  });

  const handleIncrease = (id) => {
    setSelectedId(id);
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedId && amount > 0) {
      increaseMutation.mutate({ id: selectedId, amount });
    }
  };

  const isManager = user?.role === 'MANAGER';

  if (isLoading) return <div>Loading inventory...</div>;

  return (
    <div>
      <h1>Inventory</h1>
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
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Substance</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Price</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Quantity</th>
            {isManager && <th style={{ padding: '0.75rem', textAlign: 'left' }}>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {inventory.map((item) => (
            <tr key={item.id} style={{ borderBottom: '1px solid #ddd' }}>
              <td style={{ padding: '0.75rem' }}>{item.product.name}</td>
              <td style={{ padding: '0.75rem' }}>{item.product.presentation}</td>
              <td style={{ padding: '0.75rem' }}>{item.product.substance}</td>
              <td style={{ padding: '0.75rem' }}>${item.product.price}</td>
              <td style={{ padding: '0.75rem' }}>{item.quantity}</td>
              {isManager && (
                <td style={{ padding: '0.75rem' }}>
                  <button
                    onClick={() => handleIncrease(item.id)}
                    style={{
                      background: '#27ae60',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      cursor: 'pointer',
                      borderRadius: '4px',
                    }}
                  >
                    Increase Stock
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      {isManager && selectedId && (
        <div
          style={{
            marginTop: '2rem',
            padding: '1rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            background: '#ecf0f1',
          }}
        >
          <h3>Increase Inventory</h3>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>Amount</label>
              <input
                type="number"
                min="1"
                value={amount}
                onChange={(e) => setAmount(parseInt(e.target.value))}
                required
                style={{
                  padding: '0.5rem',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                }}
              />
            </div>
            {error && (
              <div
                style={{
                  background: '#e74c3c',
                  color: 'white',
                  padding: '0.5rem',
                  borderRadius: '4px',
                  marginBottom: '1rem',
                }}
              >
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={increaseMutation.isPending}
              style={{
                background: '#3498db',
                color: 'white',
                border: 'none',
                padding: '0.5rem 1rem',
                cursor: 'pointer',
                borderRadius: '4px',
                marginRight: '0.5rem',
              }}
            >
              {increaseMutation.isPending ? 'Increasing...' : 'Confirm'}
            </button>
            <button
              type="button"
              onClick={() => setSelectedId(null)}
              style={{
                background: '#95a5a6',
                color: 'white',
                border: 'none',
                padding: '0.5rem 1rem',
                cursor: 'pointer',
                borderRadius: '4px',
              }}
            >
              Cancel
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Inventory;
