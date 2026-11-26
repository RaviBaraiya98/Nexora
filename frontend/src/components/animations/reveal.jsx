import { fadeUp } from '@/components/animations/motion-presets'
import { motion } from 'framer-motion'

export function Reveal({ children, className }) {
  return (
    <motion.div
      className={className}
      variants={fadeUp}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.2 }}
    >
      {children}
    </motion.div>
  )
}
