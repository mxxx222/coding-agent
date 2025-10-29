import { render, screen } from '@testing-library/react'
import { Hero } from '../Hero'

describe('Hero', () => {
  it('renders the main heading', () => {
    render(<Hero />)
    const heading = screen.getByRole('heading', {
      name: /The World's Most Exclusive AI Coding Tool/i,
    })
    expect(heading).toBeInTheDocument()
  })

  it('renders the description', () => {
    render(<Hero />)
    const description = screen.getByText(/Reserved for elite developers/i)
    expect(description).toBeInTheDocument()
  })

  it('renders call-to-action buttons', () => {
    render(<Hero />)
    const startButton = screen.getByRole('link', { name: /Start Premium Experience/i })
    const learnMoreButton = screen.getByRole('link', { name: /Explore Premium Features/i })

    expect(startButton).toBeInTheDocument()
    expect(learnMoreButton).toBeInTheDocument()
  })
})
