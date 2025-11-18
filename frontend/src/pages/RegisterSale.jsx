import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventoryAPI, salesAPI } from '../api';

const RegisterSale = () => {
  const queryClient = useQueryClient();
  const [items, setItems] = useState([{ product_id: '', quantity: 1 }]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const { data: inventory = [], isLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: inventoryAPI.list,
  });

  const createSaleMutation = useMutation({
    mutationFn: salesAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales'] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      setItems([{ product_id: '', quantity: 1 }]);
      setError('');
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    },
    onError: (err) => {
      setError(err.response?.data?.items?.[0] || err.response?.data?.detail || 'Failed to create sale');
    },
  });

  const handleAddItem = () => {
    setItems([...items, { product_id: '', quantity: 1 }]);
  };

  const handleRemoveItem = (index) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...items];
    newItems[index][field] = field === 'quantity' ? parseInt(value) : value;
    setItems(newItems);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    const validItems = items.filter((item) => item.product_id && item.quantity > 0);
    if (validItems.length === 0) {
      setError('Please add at least one valid item');
      return;
    }
    createSaleMutation.mutate({ items: validItems });
  };

  const calculateTotal = () => {
    return items.reduce((total, item) => {
      const inventoryItem = inventory.find((inv) => inv.product.id === parseInt(item.product_id));
      if (inventoryItem) {
        return total + parseFloat(inventoryItem.product.price) * item.quantity;
      }
      return total;
    }, 0).toFixed(2);
  };

  if (isLoading) return <div>Loading products...</div>;

  return (
    <div>
      <h1>Register Sale</h1>
      <form onSubmit={handleSubmit}>
        <div
          style={{
            marginTop: '1rem',
            padding: '1.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            background: '#ecf0f1',
          }}
        >
          <h3>Sale Items</h3>
          {items.map((item, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                gap: '1rem',
                marginBottom: '1rem',
                alignItems: 'flex-end',
              }}
            >
              <div style={{ flex: 2 }}>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Product</label>
                <select
                  value={item.product_id}
                  onChange={(e) => handleItemChange(index, 'product_id', e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                  }}
                >
                  <option value="">Select a product</option>
                  {inventory.map((inv) => (
                    <option key={inv.product.id} value={inv.product.id}>
                      {inv.product.name} - Stock: {inv.quantity} - ${inv.product.price}
                    </option>
                  ))}
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Quantity</label>
                <input
                  type="number"
                  min="1"
                  value={item.quantity}
                  onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                  }}
                />
              </div>
              <button
                type="button"
                onClick={() => handleRemoveItem(index)}
                disabled={items.length === 1}
                style={{
                  background: '#e74c3c',
                  color: 'white',
                  border: 'none',
                  padding: '0.5rem 1rem',
                  cursor: items.length === 1 ? 'not-allowed' : 'pointer',
                  borderRadius: '4px',
                  opacity: items.length === 1 ? 0.5 : 1,
                }}
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddItem}
            style={{
              background: '#27ae60',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              cursor: 'pointer',
              borderRadius: '4px',
              marginTop: '0.5rem',
            }}
          >
            Add Item
          </button>

          <div
            style={{
              marginTop: '1.5rem',
              padding: '1rem',
              background: 'white',
              borderRadius: '4px',
              fontSize: '1.2rem',
              fontWeight: 'bold',
            }}
          >
            Estimated Total: ${calculateTotal()}
          </div>
        </div>

        {error && (
          <div
            style={{
              background: '#e74c3c',
              color: 'white',
              padding: '0.5rem',
              borderRadius: '4px',
              marginTop: '1rem',
            }}
          >
            {error}
          </div>
        )}

        {success && (
          <div
            style={{
              background: '#27ae60',
              color: 'white',
              padding: '0.5rem',
              borderRadius: '4px',
              marginTop: '1rem',
            }}
          >
            Sale registered successfully!
          </div>
        )}

        <button
          type="submit"
          disabled={createSaleMutation.isPending}
          style={{
            background: '#3498db',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            cursor: 'pointer',
            borderRadius: '4px',
            marginTop: '1rem',
            fontSize: '1rem',
          }}
        >
          {createSaleMutation.isPending ? 'Processing...' : 'Complete Sale'}
        </button>
      </form>
    </div>
  );
};

export default RegisterSale;
