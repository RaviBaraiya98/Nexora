import { useEffect, useState } from 'react'

export function AnimatedCounter({ value = 0, duration = 900 }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    const steps = 30
    const increment = value / steps
    const stepTime = duration / steps
    let current = 0

    const timer = setInterval(() => {
      current += increment
      if (current >= value) {
        setCount(value)
        clearInterval(timer)
      } else {
        setCount(Math.round(current))
      }
    }, stepTime)

    return () => clearInterval(timer)
  }, [value, duration])

  return <span>{count}</span>
}
