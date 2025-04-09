"use client"

import { useState } from "react"
import { Check, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

export default function JobSelector({ jobs, selectedJob, onSelectJob }) {
  const [open, setOpen] = useState(false)

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[280px] justify-between bg-slate-800/50 border-slate-700 text-slate-200 hover:bg-slate-700/50"
        >
          {selectedJob ? selectedJob.title : "Select job..."}
          <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[280px] p-0 bg-slate-800 border-slate-700">
        <Command className="bg-transparent">
          <CommandInput placeholder="Search jobs..." className="text-slate-200" />
          <CommandList>
            <CommandEmpty>No job found.</CommandEmpty>
            <CommandGroup>
              {jobs.map((job) => (
                <CommandItem
                  key={job.id}
                  value={job.id}
                  onSelect={() => {
                    onSelectJob(job)
                    setOpen(false)
                  }}
                  className="text-slate-200 hover:bg-slate-700"
                >
                  <Check
                    className={`mr-2 h-4 w-4 ${selectedJob?.id === job.id ? "opacity-100 text-cyan-500" : "opacity-0"}`}
                  />
                  {job.title}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

