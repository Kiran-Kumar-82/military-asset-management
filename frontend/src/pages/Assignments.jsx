import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'
import api from '../services/api'
import { format } from 'date-fns'

export default function Assignments() {
  const [assignments, setAssignments] = useState([])
  const [bases, setBases] = useState([])
  const [assetTypes, setAssetTypes] = useState([])
  const [loading, setLoading] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingAssignment, setEditingAssignment] = useState(null)
  const [formData, setFormData] = useState({
    base: '',
    asset_type: '',
    quantity: '',
    assigned_to: '',
    assignment_date: new Date(),
    return_date: null,
    status: 'active',
    notes: '',
  })

  useEffect(() => {
    fetchAssignments()
    fetchBases()
    fetchAssetTypes()
  }, [])

  const fetchAssignments = async () => {
    setLoading(true)
    try {
      const response = await api.get('/assets/assignments/')
      setAssignments(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch assignments:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchBases = async () => {
    try {
      const response = await api.get('/assets/bases/')
      setBases(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch bases:', error)
    }
  }

  const fetchAssetTypes = async () => {
    try {
      const response = await api.get('/assets/asset-types/')
      setAssetTypes(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch asset types:', error)
    }
  }

  const handleOpenDialog = (assignment = null) => {
    if (assignment) {
      setEditingAssignment(assignment)
      setFormData({
        base: assignment.base,
        asset_type: assignment.asset_type,
        quantity: assignment.quantity,
        assigned_to: assignment.assigned_to,
        assignment_date: new Date(assignment.assignment_date),
        return_date: assignment.return_date ? new Date(assignment.return_date) : null,
        status: assignment.status,
        notes: assignment.notes || '',
      })
    } else {
      setEditingAssignment(null)
      setFormData({
        base: '',
        asset_type: '',
        quantity: '',
        assigned_to: '',
        assignment_date: new Date(),
        return_date: null,
        status: 'active',
        notes: '',
      })
    }
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingAssignment(null)
  }

  const handleSubmit = async () => {
    try {
      const data = {
        ...formData,
        assignment_date: format(formData.assignment_date, 'yyyy-MM-dd'),
        return_date: formData.return_date
          ? format(formData.return_date, 'yyyy-MM-dd')
          : null,
      }
      if (editingAssignment) {
        await api.put(`/assets/assignments/${editingAssignment.id}/`, data)
      } else {
        await api.post('/assets/assignments/', data)
      }
      handleCloseDialog()
      fetchAssignments()
    } catch (error) {
      console.error('Failed to save assignment:', error)
      alert('Failed to save assignment: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this assignment?')) {
      try {
        await api.delete(`/assets/assignments/${id}/`)
        fetchAssignments()
      } catch (error) {
        console.error('Failed to delete assignment:', error)
        alert('Failed to delete assignment')
      }
    }
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4">Assignments</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            New Assignment
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Base</TableCell>
                <TableCell>Asset Type</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Assigned To</TableCell>
                <TableCell>Assignment Date</TableCell>
                <TableCell>Return Date</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {assignments.map((assignment) => (
                <TableRow key={assignment.id}>
                  <TableCell>{assignment.base_name}</TableCell>
                  <TableCell>{assignment.asset_type_name}</TableCell>
                  <TableCell>{assignment.quantity}</TableCell>
                  <TableCell>{assignment.assigned_to}</TableCell>
                  <TableCell>{assignment.assignment_date}</TableCell>
                  <TableCell>{assignment.return_date || 'N/A'}</TableCell>
                  <TableCell>{assignment.status}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(assignment)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(assignment.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingAssignment ? 'Edit Assignment' : 'New Assignment'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <TextField
                select
                label="Base"
                value={formData.base}
                onChange={(e) => setFormData({ ...formData, base: e.target.value })}
                fullWidth
                required
              >
                {bases.map((base) => (
                  <MenuItem key={base.id} value={base.id}>
                    {base.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Asset Type"
                value={formData.asset_type}
                onChange={(e) =>
                  setFormData({ ...formData, asset_type: e.target.value })
                }
                fullWidth
                required
              >
                {assetTypes.map((type) => (
                  <MenuItem key={type.id} value={type.id}>
                    {type.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                label="Quantity"
                type="number"
                value={formData.quantity}
                onChange={(e) =>
                  setFormData({ ...formData, quantity: e.target.value })
                }
                fullWidth
                required
              />
              <TextField
                label="Assigned To"
                value={formData.assigned_to}
                onChange={(e) =>
                  setFormData({ ...formData, assigned_to: e.target.value })
                }
                fullWidth
                required
              />
              <DatePicker
                label="Assignment Date"
                value={formData.assignment_date}
                onChange={(date) =>
                  setFormData({ ...formData, assignment_date: date })
                }
                slotProps={{
                  textField: {
                    fullWidth: true,
                  },
                }}
              />
              <DatePicker
                label="Return Date (Optional)"
                value={formData.return_date}
                onChange={(date) =>
                  setFormData({ ...formData, return_date: date })
                }
                slotProps={{
                  textField: {
                    fullWidth: true,
                  },
                }}
              />
              <TextField
                select
                label="Status"
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value })
                }
                fullWidth
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="returned">Returned</MenuItem>
                <MenuItem value="lost">Lost</MenuItem>
              </TextField>
              <TextField
                label="Notes"
                multiline
                rows={3}
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                fullWidth
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button onClick={handleSubmit} variant="contained">
              {editingAssignment ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  )
}

