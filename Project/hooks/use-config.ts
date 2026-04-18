import { useState, useEffect } from "react"

interface Config {
  target_col: string
  sensitive_col: string
}

export function useConfig() {
  const [config, setConfig] = useState<Config>({ target_col: "Income", sensitive_col: "Sex" })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchConfig() {
      try {
        const response = await fetch("http://127.0.0.1:8001/api/config")
        if (response.ok) {
          const json = await response.json()
          setConfig({
            target_col: json.target_col || "Income",
            sensitive_col: json.sensitive_col || "Sex"
          })
        }
      } catch (err) {
        console.error("Failed to fetch config, using defaults.")
      } finally {
        setLoading(false)
      }
    }
    fetchConfig()
  }, [])

  return { config, loading }
}
