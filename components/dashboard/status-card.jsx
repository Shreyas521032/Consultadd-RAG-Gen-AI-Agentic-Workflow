import { ArrowDown, ArrowUp } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

export default function StatusCard({ title, value, icon: Icon, color, trend }) {
  const getColor = () => {
    switch (color) {
      case "cyan":
        return "from-cyan-500 to-blue-500 border-cyan-500/30"
      case "green":
        return "from-green-500 to-emerald-500 border-green-500/30"
      case "amber":
        return "from-amber-500 to-yellow-500 border-amber-500/30"
      case "red":
        return "from-red-500 to-pink-500 border-red-500/30"
      case "blue":
        return "from-blue-500 to-indigo-500 border-blue-500/30"
      default:
        return "from-cyan-500 to-blue-500 border-cyan-500/30"
    }
  }

  const getTrendIcon = () => {
    if (trend?.direction === "up") {
      return <ArrowUp className="h-4 w-4 text-green-500" />
    } else if (trend?.direction === "down") {
      return <ArrowDown className="h-4 w-4 text-red-500" />
    }
    return null
  }

  return (
    <Card className={`bg-slate-800/50 rounded-lg border ${getColor()} relative overflow-hidden`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-slate-400">{title}</div>
          <Icon className={`h-5 w-5 text-${color}-500`} />
        </div>
        <div className="text-2xl font-bold mb-1 bg-gradient-to-r bg-clip-text text-transparent from-slate-100 to-slate-300">
          {value}
        </div>
        {trend && (
          <div className="flex items-center text-xs">
            {getTrendIcon()}
            <span className={trend.direction === "up" ? "text-green-500" : "text-red-500"}>
              {trend.value} from last week
            </span>
          </div>
        )}
        <div className="absolute -bottom-6 -right-6 h-16 w-16 rounded-full bg-gradient-to-r opacity-20 blur-xl from-cyan-500 to-blue-500"></div>
      </CardContent>
    </Card>
  )
}

