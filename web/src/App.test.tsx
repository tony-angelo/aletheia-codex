import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders loading state initially', () => {
  render(<App />);
  const loadingElement = screen.getByText(/Loading application/i);
  expect(loadingElement).toBeInTheDocument();
});

test('renders sign in button when not authenticated', () => {
  render(<App />);
  
  // Use getByRole to get the button specifically, not text
  const signInButton = screen.getByRole('button', { name: /sign in/i });
  expect(signInButton).toBeInTheDocument();
});