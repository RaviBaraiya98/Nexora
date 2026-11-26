import { TopNav } from '@/components/layout/top-nav'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { targetCompanies } from '@/constants/mock-data'
import { usePageTitle } from '@/hooks/use-page-title'
import { motion } from 'framer-motion'
import { Search } from 'lucide-react'
import { useMemo, useState } from 'react'

export function CompaniesPage() {
  usePageTitle('Companies')
  const [query, setQuery] = useState('')

  const companies = useMemo(
    () => targetCompanies.filter((item) => item.name.toLowerCase().includes(query.toLowerCase())),
    [query],
  )

  return (
    <div>
      <TopNav title="Company Prep Intelligence" subtitle="Search targets, inspect expected rounds, start focused prep" />

      <div className="mb-6 border-b border-border pb-6"><p className="eyebrow">Company intelligence / target map</p><p className="mt-3 max-w-2xl font-display text-3xl text-foreground">Choose a target. Nexora will expose the preparation context behind it.</p></div>
      <div className="mb-4 flex flex-wrap gap-3">
        <div className="relative w-full max-w-sm">
          <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input value={query} onChange={(event) => setQuery(event.target.value)} className="pl-9" placeholder="Search company" />
        </div>
        <Badge>Top Tier</Badge>
        <Badge>Remote Friendly</Badge>
        <Badge>Product Engineering</Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {companies.map((item) => (
          <motion.div key={item.name} whileHover={{ y: -3 }} transition={{ duration: 0.2 }}>
          <Card>
            <CardHeader>
              <CardTitle>{item.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p className="font-data text-xs text-accent">{item.role}</p>
              <p>Expected Rounds: {item.rounds}</p>
              <p>Focus: {item.focus}</p>
              <div className="border-t border-border pt-3"><p className="eyebrow">Preparation priority</p><p className="mt-2 text-xs leading-5">{item.focus}</p></div>
              <Button variant="outline" className="w-full">Build preparation path</Button>
            </CardContent>
          </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
