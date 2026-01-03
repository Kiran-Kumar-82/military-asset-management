import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  TextField,
  MenuItem,
  Button,
  Card,
  CardContent,
  Modal,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { format } from 'date-fns'

const modalStyle = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 500,
  bgcolor: 'background.paper',
  boxShadow: 24,
  p: 4,
}

export default function Dashboard() {
  const { user } = useAuth()
  const [dashboardData, setDashboardData] = useState([])
  const [bases, setBases] = useState([])
  const [assetTypes, setAssetTypes] = useState([])
  const [filters, setFilters] = useState({
    base_id: '',
    asset_type_id: '',
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    end_date: new Date(),
  })
  const [loading, setLoading] = useState(false)
  const [selectedNetMovement, setSelectedNetMovement] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)

  useEffect(() => {
    fetchBases()
    fetchAssetTypes()
  }, [])

  useEffect(() => {
    fetchDashboardData()
  }, [filters])

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

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      const params = {
        base_id: filters.base_id || undefined,
        asset_type_id: filters.asset_type_id || undefined,
        start_date: format(filters.start_date, 'yyyy-MM-dd'),
        end_date: format(filters.end_date, 'yyyy-MM-dd'),
      }
      const response = await api.get('/assets/dashboard/data/', { params })
      setDashboardData(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNetMovementClick = (data) => {
    setSelectedNetMovement(data)
    setModalOpen(true)
  }

  const calculateTotals = () => {
    return dashboardData.reduce(
      (acc, item) => ({
        opening_balance: acc.opening_balance + item.opening_balance,
        closing_balance: acc.closing_balance + item.closing_balance,
        net_movement: acc.net_movement + item.net_movement,
        assigned_assets: acc.assigned_assets + item.assigned_assets,
        expended_assets: acc.expended_assets + item.expended_assets,
      }),
      {
        opening_balance: 0,
        closing_balance: 0,
        net_movement: 0,
        assigned_assets: 0,
        expended_assets: 0,
      }
    )
  }

  const totals = calculateTotals()

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>

        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                label="Base"
                value={filters.base_id}
                onChange={(e) =>
                  setFilters({ ...filters, base_id: e.target.value })
                }
              >
                <MenuItem value="">All Bases</MenuItem>
                {bases.map((base) => (
                  <MenuItem key={base.id} value={base.id}>
                    {base.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                label="Asset Type"
                value={filters.asset_type_id}
                onChange={(e) =>
                  setFilters({ ...filters, asset_type_id: e.target.value })
                }
              >
                <MenuItem value="">All Asset Types</MenuItem>
                {assetTypes.map((type) => (
                  <MenuItem key={type.id} value={type.id}>
                    {type.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <DatePicker
                label="Start Date"
                value={filters.start_date}
                onChange={(date) =>
                  setFilters({ ...filters, start_date: date })
                }
                slotProps={{
                  textField: {
                    fullWidth: true,
                  },
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <DatePicker
                label="End Date"
                value={filters.end_date}
                onChange={(date) =>
                  setFilters({ ...filters, end_date: date })
                }
                slotProps={{
                  textField: {
                    fullWidth: true,
                  },
                }}
              />
            </Grid>
          </Grid>
        </Paper>

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Opening Balance
                </Typography>
                <Typography variant="h4">
                  {totals.opening_balance.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Closing Balance
                </Typography>
                <Typography variant="h4">
                  {totals.closing_balance.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Net Movement
                </Typography>
                <Typography variant="h4">
                  {totals.net_movement.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Assigned Assets
                </Typography>
                <Typography variant="h4">
                  {totals.assigned_assets.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Expended Assets
                </Typography>
                <Typography variant="h4">
                  {totals.expended_assets.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Base</TableCell>
                <TableCell>Asset Type</TableCell>
                <TableCell>Opening Balance</TableCell>
                <TableCell>Closing Balance</TableCell>
                <TableCell>Net Movement</TableCell>
                <TableCell>Assigned</TableCell>
                <TableCell>Expended</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {dashboardData.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{item.base_name}</TableCell>
                  <TableCell>{item.asset_type_name}</TableCell>
                  <TableCell>{item.opening_balance.toFixed(2)}</TableCell>
                  <TableCell>{item.closing_balance.toFixed(2)}</TableCell>
                  <TableCell>
                    <Button
                      variant="text"
                      onClick={() => handleNetMovementClick(item)}
                    >
                      {item.net_movement.toFixed(2)}
                    </Button>
                  </TableCell>
                  <TableCell>{item.assigned_assets.toFixed(2)}</TableCell>
                  <TableCell>{item.expended_assets.toFixed(2)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
          <Box sx={modalStyle}>
            <Typography variant="h6" gutterBottom>
              Net Movement Details
            </Typography>
            {selectedNetMovement && (
              <Box>
                <Typography variant="body1" gutterBottom>
                  <strong>Base:</strong> {selectedNetMovement.base_name}
                </Typography>
                <Typography variant="body1" gutterBottom>
                  <strong>Asset Type:</strong> {selectedNetMovement.asset_type_name}
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell>Purchases</TableCell>
                        <TableCell>
                          {selectedNetMovement.net_movement_details.purchases.toFixed(2)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Transfers In</TableCell>
                        <TableCell>
                          {selectedNetMovement.net_movement_details.transfers_in.toFixed(2)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Transfers Out</TableCell>
                        <TableCell>
                          {selectedNetMovement.net_movement_details.transfers_out.toFixed(2)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>
                          <strong>Net Movement</strong>
                        </TableCell>
                        <TableCell>
                          <strong>
                            {selectedNetMovement.net_movement.toFixed(2)}
                          </strong>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
                <Button
                  variant="contained"
                  onClick={() => setModalOpen(false)}
                  sx={{ mt: 2 }}
                >
                  Close
                </Button>
              </Box>
            )}
          </Box>
        </Modal>
      </Box>
    </LocalizationProvider>
  )
}

