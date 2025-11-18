import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productAPI } from '../api';

const Products = () => {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    presentation: 'tablets',
    substance: '',
    price: '',
  });
  const [error, setError] = useState('');

  const { data: products = [], isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: productAPI.list,
  });

  const createMutation = useMutation({
    mutationFn: productAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      resetForm();
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Failed to create product');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => productAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      resetForm();
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Failed to update product');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: productAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });

  const resetForm = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData({ name: '', presentation: 'tablets', substance: '', price: '' });
    setError('');
  };

  const handleEdit = (product) => {
    setEditingId(product.id);
    setFormData({
      name: product.name,
      presentation: product.presentation,
      substance: product.substance,
      price: product.price,
    });
    setShowForm(true);
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (id) => {
    if (confirm('Are you sure you want to delete this product?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div>Loading products...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Products</h1>
        <button
          onClick={() => setShowForm(true)}
          style={{
            background: '#27ae60',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            cursor: 'pointer',
            borderRadius: '4px',
          }}
        >
          Add Product
        </button>
      </div>

      {showForm && (
        <div
          style={{
            marginTop: '1rem',
            padding: '1.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            background: '#ecf0f1',
          }}
        >
          <h3>{editingId ? 'Edit Product' : 'Add Product'}</h3>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                }}
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>Presentation</label>
              <select
                value={formData.presentation}
                onChange={(e) => setFormData({ ...formData, presentation: e.target.value })}
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                }}
              >
                <option value="tablets">Tablets</option>
                <option value="capsules">Capsules</option>
                <option value="syrups">Syrups</option>
                <option value="suspensions">Suspensions</option>
                <option value="solutions">Solutions</option>
                <option value="pills">Pills</option>
                <option value="injectables">Injectables</option>
              </select>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>Substance</label>
              <input
                type="text"
                value={formData.substance}
                onChange={(e) => setFormData({ ...formData, substance: e.target.value })}
                required
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                }}
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>Price</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                required
                style={{
                  width: '100%',
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
              disabled={createMutation.isPending || updateMutation.isPending}
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
              {createMutation.isPending || updateMutation.isPending ? 'Saving...' : 'Save'}
            </button>
            <button
              type="button"
              onClick={resetForm}
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

      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          marginTop: '1rem',
        }}
      >
        <thead>
          <tr style={{ background: '#34495e', color: 'white' }}>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Name</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Presentation</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Substance</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Price</th>
            <th style={{ padding: '0.75rem', textAlign: 'left' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.id} style={{ borderBottom: '1px solid #ddd' }}>
              <td style={{ padding: '0.75rem' }}>{product.name}</td>
              <td style={{ padding: '0.75rem' }}>{product.presentation}</td>
              <td style={{ padding: '0.75rem' }}>{product.substance}</td>
              <td style={{ padding: '0.75rem' }}>${product.price}</td>
              <td style={{ padding: '0.75rem' }}>
                <button
                  onClick={() => handleEdit(product)}
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
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(product.id)}
                  disabled={deleteMutation.isPending}
                  style={{
                    background: '#e74c3c',
                    color: 'white',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    cursor: 'pointer',
                    borderRadius: '4px',
                  }}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Products;
