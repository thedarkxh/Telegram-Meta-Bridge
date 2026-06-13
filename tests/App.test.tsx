import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import App from '../src/App';

describe('Self-Assessment Portal Render Smoke Tests', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders application sidebar successfully', () => {
    render(<App />);

    // Verify application brand displays in sidebar
    expect(screen.getByText('Self-Assess')).toBeInTheDocument();
    
    // Verify navigation buttons exist
    expect(screen.getByRole('button', { name: /^dashboard$/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^my notes$/i })).toBeInTheDocument();
  });

  it('renders Dashboard as default active view', () => {
    render(<App />);

    // The Dashboard component should render a metrics summary or heading
    expect(screen.getByText('Dashboard Overview')).toBeInTheDocument();
    expect(screen.getByText('Total Study Notes')).toBeInTheDocument();
  });

  it('navigates successfully to Notes List view when clicked', () => {
    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    expect(notesTab).toBeInTheDocument();

    // Click My Notes button
    fireEvent.click(notesTab);

    // Verify Notes List is displayed
    expect(screen.getByText('My Study Notes')).toBeInTheDocument();
    expect(screen.getByText('Browse, search, and manage your notes.')).toBeInTheDocument();
  });
});
